# Solicitar acceso a los repos plantilla de Diseño Biomédico 1

Repo público para solicitar acceso de lectura a
[`DisenoBiomedico-1/Plantilla-Diseno1`](https://github.com/DisenoBiomedico-1/Plantilla-Diseno1)
y [`DisenoBiomedico-1/curso-admin`](https://github.com/DisenoBiomedico-1/curso-admin),
paso previo para replicar el sistema de gestión del curso en una organización de GitHub
propia (ver la guía en [disenobiomedico-1.github.io/curso-admin](https://disenobiomedico-1.github.io/curso-admin/)).

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
