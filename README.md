# Solicitar acceso a los repos plantilla de Diseño Biomédico 1

Repo público para solicitar acceso de lectura a
[`DisenoBiomedico-1/Plantilla-Diseno1`](https://github.com/DisenoBiomedico-1/Plantilla-Diseno1)
y [`DisenoBiomedico-1/curso-admin`](https://github.com/DisenoBiomedico-1/curso-admin),
paso previo para replicar el sistema de gestión del curso en una organización de GitHub
propia. La guía paso a paso y el script de bootstrap están publicados desde este mismo
repo, en [disenobiomedico-1.github.io/Solicitar-Acceso](https://disenobiomedico-1.github.io/Solicitar-Acceso/)
(`docs/index.html`, vía GitHub Pages).

## Cómo solicitar acceso

1. [Abrí un issue nuevo con el formulario de solicitud](../../issues/new?template=solicitud-acceso.yml).
2. Completá tu usuario de GitHub, nombre e institución/curso.
3. Un administrador de `DisenoBiomedico-1` revisa la solicitud y, si la aprueba, le agrega
   la etiqueta `aprobado` al issue.

## Qué pasa después de la aprobación

Al agregar la etiqueta `aprobado`, `.github/workflows/otorgar-acceso.yml` corre
automáticamente: agrega al usuario solicitante como colaborador de lectura (permiso
`pull`) en `Plantilla-Diseno1` y `curso-admin`, comenta en el issue confirmando el acceso,
y lo cierra. El usuario recibe la invitación de colaborador por notificación de GitHub.

## Por qué existe este repo separado

`curso-admin` es privado y va a contener, con el tiempo, usuarios reales de estudiantes
en sus rosters. No se puede abrir a solicitudes públicas de acceso ahí directamente: un
no-colaborador no puede abrir issues en un repo privado. Este repo, público, resuelve el
punto de entrada sin exponer nada de `curso-admin`; el otorgamiento de acceso sigue
requiriendo la aprobación explícita de un administrador (agregar la etiqueta `aprobado`
requiere permiso de escritura o triage sobre este repo).

## Por qué la guía y el script viven acá y no en `curso-admin`

`curso-admin` es un repo plantilla (`is_template: true`): cada copia que alguien genera
con "Use this template" se lleva todo su contenido. Si la guía "cómo replicar este
sistema" viviera en `curso-admin`, cada copia resultante arrastraría esa guía adentro,
sin ningún uso una vez que ya replicó. Este repo no es plantilla, así que no tiene ese
problema, y ya era el punto de entrada público natural para quien quiere empezar a
replicar.
