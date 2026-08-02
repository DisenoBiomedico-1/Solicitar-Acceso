#!/usr/bin/env python3
"""
Bootstrap: termina de configurar tu copia de curso-admin, ya clonada en tu
propia organización de GitHub, automatizando todo lo que la API de GitHub
permite automatizar.

Qué SÍ hace este script (una vez que ya generaste tus copias con "Use this
template" y tenés tu token):
  1. Reemplaza el nombre de la org de origen por el de la tuya en los
     scripts de tu copia de curso-admin (find-and-replace, preservando el
     permiso de ejecución de cada .sh).
  2. Crea el secret ORG_ADMIN_TOKEN en tu copia de curso-admin, con el
     mismo token que le pasaste a este script (cifrado como exige GitHub).
  3. Configura los privilegios de tu org (base permissions "No permissions",
     repos nuevos de miembros solo privados, forking de repos privados
     desactivado).

Qué NO puede hacer (y por qué; esto es una limitación de GitHub, no del
script, así que no tiene sentido tratar de automatizarlo):
  - Crear la organización. GitHub no tiene API pública para eso.
  - Generar tu Personal Access Token. Requiere confirmación manual tuya en
    el navegador (es, a propósito, imposible de automatizar del todo: es
    la barrera de seguridad que evita que un script cree credenciales de
    administrador sin que un humano lo apruebe).
  - Generar tus copias de Plantilla-Diseno1 y curso-admin ("Use this
    template"). Un fine-grained PAT queda atado a un único resource owner
    (tu org nueva); no puede leer nada de DisenoBiomedico-1, aunque seas
    colaborador de lectura ahí con tu cuenta. Ese acceso de colaborador
    vale para tu sesión de navegador, no para un token con otro resource
    owner. Por eso "Use this template" es un paso manual, en los dos
    caminos (automático y manual) por igual.
  - Completar tus rosters de estudiantes ni las fechas reales del
    semestre: eso es información que solo vos tenés.

Requisitos previos (ver https://disenobiomedico-1.github.io/Solicitar-Acceso/, Pasos 1 a 3,
antes de correr esto):
  - Ya creaste tu organización en GitHub.
  - Ya generaste tus copias de Plantilla-Diseno1 y curso-admin en tu org, con
    "Use this template" (necesitás acceso de lectura a los repos de origen
    para ese paso puntual; no lo necesita este script).
  - Ya generaste tu fine-grained PAT (Organización -> Administration, Projects:
    R/W; Repositorio -> Administration, Contents, Issues, Secrets, Workflows:
    R/W; resource owner = tu org nueva; repository access = All repositories).

Instalación de dependencias:
    pip install requests pynacl

Uso:
    python3 replicar_en_tu_org.py --org TU-ORG --token TU_TOKEN

    (si no pasás --token, lo pide de forma oculta con getpass, para no
    dejarlo en el historial de la terminal)
"""

import argparse
import base64
import getpass
import sys

try:
    import requests
except ImportError:
    sys.exit("Falta la librería 'requests'. Instalala con: pip install requests")

try:
    from nacl import encoding, public
except ImportError:
    sys.exit("Falta la librería 'pynacl'. Instalala con: pip install pynacl")

TEMPLATE_OWNER = "DisenoBiomedico-1"
TEMPLATE_REPOS = ["Plantilla-Diseno1", "curso-admin"]
CURSO_ADMIN_REPO = "curso-admin"

# Archivos de curso-admin donde el nombre de la org de origen está
# hardcodeado como variable, y hay que reemplazarlo por el de la org nueva.
ARCHIVOS_CON_ORG = [
    "scripts/crear_repos_grupos.sh",
    "scripts/reasignar_certificados.sh",
    "scripts/vincular_project.sh",
    "scripts/listar_projects.sh",
    "scripts/agregar_estudiante.sh",
    "scripts/borrar_projects.sh",
    "scripts/borrar_repo.sh",
    "scripts/crear_project.sh",
    ".github/workflows/actualizar-fechas.yml",
]

API = "https://api.github.com"


class GitHub:
    def __init__(self, token):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def get(self, path, **kw):
        r = self.session.get(f"{API}{path}", **kw)
        return r

    def put(self, path, **kw):
        r = self.session.put(f"{API}{path}", **kw)
        return r

    def patch(self, path, **kw):
        r = self.session.patch(f"{API}{path}", **kw)
        return r


def verificar_acceso(gh, org):
    r = gh.get("/user")
    if r.status_code != 200:
        sys.exit(f"✗ El token no es válido (HTTP {r.status_code}): {r.text[:200]}")
    usuario = r.json()["login"]
    print(f"+ Token válido para el usuario: {usuario}")

    r = gh.get(f"/orgs/{org}")
    if r.status_code != 200:
        sys.exit(
            f"✗ No se pudo acceder a la organización '{org}' (HTTP {r.status_code}). "
            "¿Existe? ¿El token tiene ese resource owner?"
        )
    print(f"+ Organización encontrada: {org}")

    for repo in TEMPLATE_REPOS:
        r = gh.get(f"/repos/{org}/{repo}")
        if r.status_code != 200:
            sys.exit(
                f"✗ No existe {org}/{repo} (HTTP {r.status_code}). Generalo primero con "
                f"\"Use this template\" desde {TEMPLATE_OWNER}/{repo} (paso manual, "
                "este script no puede hacerlo: ver la nota en --help)."
            )
        print(f"+ {org}/{repo} existe.")


def reemplazar_org_en_archivo(gh, org, repo, path):
    r = gh.get(f"/repos/{org}/{repo}/contents/{path}")
    if r.status_code != 200:
        print(f"  ! No se pudo leer {path} (HTTP {r.status_code}), se omite.")
        return

    data = r.json()
    contenido = base64.b64decode(data["content"]).decode("utf-8")

    if TEMPLATE_OWNER not in contenido:
        print(f"  -- {path}: no contiene '{TEMPLATE_OWNER}', se omite.")
        return

    nuevo_contenido = contenido.replace(TEMPLATE_OWNER, org)
    nuevo_b64 = base64.b64encode(nuevo_contenido.encode("utf-8")).decode("ascii")

    r = gh.put(
        f"/repos/{org}/{repo}/contents/{path}",
        json={
            "message": f"chore: adaptar org a {org}",
            "content": nuevo_b64,
            "sha": data["sha"],
        },
    )
    if r.status_code in (200, 201):
        print(f"  + {path}: org reemplazada.")
    else:
        print(f"  ✗ {path}: no se pudo actualizar (HTTP {r.status_code}).")


def adaptar_org_en_scripts(gh, org):
    print(f"\n== Adaptando el nombre de la org en {org}/{CURSO_ADMIN_REPO} ==")
    for path in ARCHIVOS_CON_ORG:
        reemplazar_org_en_archivo(gh, org, CURSO_ADMIN_REPO, path)


def crear_secret_org_admin_token(gh, org, token):
    print(f"\n== Creando el secret ORG_ADMIN_TOKEN en {org}/{CURSO_ADMIN_REPO} ==")
    r = gh.get(f"/repos/{org}/{CURSO_ADMIN_REPO}/actions/secrets/public-key")
    if r.status_code != 200:
        print(f"  ✗ No se pudo obtener la public key del repo (HTTP {r.status_code}).")
        return

    key_data = r.json()
    public_key = public.PublicKey(key_data["key"], encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(token.encode("utf-8"))
    encrypted_b64 = base64.b64encode(encrypted).decode("ascii")

    r = gh.put(
        f"/repos/{org}/{CURSO_ADMIN_REPO}/actions/secrets/ORG_ADMIN_TOKEN",
        json={"encrypted_value": encrypted_b64, "key_id": key_data["key_id"]},
    )
    if r.status_code in (201, 204):
        print("  + Secret ORG_ADMIN_TOKEN creado.")
    else:
        print(f"  ✗ No se pudo crear el secret (HTTP {r.status_code}). Creálo a mano en Settings.")


def configurar_privilegios_org(gh, org):
    print(f"\n== Configurando privilegios de {org} ==")
    r = gh.patch(
        f"/orgs/{org}",
        json={
            "default_repository_permission": "none",
            "members_can_create_public_repositories": False,
            "members_can_create_private_repositories": True,
            "members_can_fork_private_repositories": False,
        },
    )
    if r.status_code == 200:
        print("  + Base permissions: 'No permissions'.")
        print("  + Repos nuevos de miembros: solo privados.")
        print("  + Forking de repos privados: desactivado.")
        return

    if r.status_code == 422 and "Private-only repository creation" in r.text:
        # GitHub Free para organizaciones no permite restringir "Repository
        # creation" a solo privados (eso es una función de planes pagos).
        # Se aplica lo que sí es posible en el plan gratuito, y se avisa
        # claramente qué quedó sin poder configurarse.
        print(
            "  ! El plan de tu organización no permite restringir 'Repository "
            "creation' a solo privados (requiere plan Team o superior). Se "
            "aplica el resto de los privilegios sin esa restricción."
        )
        r2 = gh.patch(
            f"/orgs/{org}",
            json={
                "default_repository_permission": "none",
                "members_can_fork_private_repositories": False,
            },
        )
        if r2.status_code == 200:
            print("  + Base permissions: 'No permissions'.")
            print("  + Forking de repos privados: desactivado.")
            print(
                "  ! Repository creation quedó sin cambios (Settings -> Member "
                "privileges): revisalo a mano si te importa acotarlo."
            )
        else:
            print(f"  ✗ Tampoco se pudo aplicar el resto (HTTP {r2.status_code}).")
            print(f"    Detalle de GitHub: {r2.text[:500]}")
        return

    print(
        f"  ✗ No se pudieron configurar los privilegios (HTTP {r.status_code}). "
        "Revisalo a mano en Settings -> Member privileges. "
        "(Nota: este endpoint requiere que seas Owner de la org, no alcanza con Administration del token.)"
    )
    print(f"    Detalle de GitHub: {r.text[:500]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--org", required=True, help="Nombre de tu organización nueva en GitHub")
    parser.add_argument("--token", help="Tu fine-grained PAT (si se omite, se pide de forma oculta)")
    args = parser.parse_args()

    token = args.token or getpass.getpass("Pegá tu fine-grained PAT (no se muestra en pantalla): ")
    gh = GitHub(token)

    verificar_acceso(gh, args.org)
    adaptar_org_en_scripts(gh, args.org)
    crear_secret_org_admin_token(gh, args.org, token)
    configurar_privilegios_org(gh, args.org)

    print(
        f"""
== Listo. Lo que sigue es manual (son datos que solo vos tenés) ==

1. Completá los roster CSVs en {args.org}/{CURSO_ADMIN_REPO}/roster/
2. Completá las fechas reales del semestre en
   {args.org}/{CURSO_ADMIN_REPO}/scripts/issues_iniciales/fechas-retos.csv
3. Probá el flujo con una fila de prueba antes de usarlo con estudiantes
   reales (Actions -> crear-repos-grupos.yml -> Run workflow).

Ver https://disenobiomedico-1.github.io/Solicitar-Acceso/, Paso 8 en adelante, para el
detalle de cada uno.
"""
    )


if __name__ == "__main__":
    main()
