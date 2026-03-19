# CertiDigital.API.Sample

## Puesta en marcha (clonado desde GitHub)
1. Instala Python 3 y `pip`.
2. Crea y activa un entorno virtual.
3. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura acceso a la api en el fichero `src/data/auth.json` (clientId, clientSecret, username, password, tokenUrl, logoutUrl). 
    - Puedes usar la plantilla `src/data/authTemplate.json`. Las credenciales las deberías conocer. 
5. Configura parametros en `src/data/params.json`:
    - `emission_block_size`: tamano de los bloques de emision (default: 25).
    - `downloadCredentials`: `true/false` para descargar PDF/JSON-LD (default: false).
    - `organization_id`: id de la organizacion awarding (default: 1).
    - `issuing_center`: id del centro emisor (default: 1).
    - `diploma_id`: id del diploma existente (default: 1).
6. Ten en cuenta que los tests usan rutas absolutas basadas en tu `HOME`:
   - `Path.home()/PycharmProjects/CertiDigital.API.Sample/...`
   Si has clonado el proyecto en otra ruta, actualiza `__path_data` y `__path_output` en los tests o crea un enlace simbolico.
7. Asegura los prerequisitos en la plataforma CertiDigital:
   - Existe universidad e issuing center (id conocido) asociados al usuario.
   - Existe una organizacion awarding (id conocido).
   - Existe un diploma (id conocido) para enlazar con la credencial.
8. Ejecuta los tests (en este orden, el primero crea la plantilla de la credencial, el segundo emite, envía, sella...):
   ```bash
   python -m unittest src/unittest/python/test_advanced_credential_creation_tests.py
   python -m unittest src/unittest/python/test_advanced_credential_emission_tests.py
   ```

## Detalle de los Tests existentes

### `test_advanced_credential_creation_tests.py`
Test de integracion que crea una credencial avanzada completa.

Lo que hace:
- Autentica contra la API y limpia entidades previas leyendo `src/data/advancedcredential/idlist.json`.
- Obtiene info del usuario y usa ids conocidos para:
  - `issuing_center` (hardcoded en el test).
  - `organization_id` (awarding organization).
  - `diploma_id` (diploma existente).
- Crea actividades, evaluaciones, learning outcomes y logros (achievements) desde los JSON en `src/data/advancedcredential/`.
- Relaciona actividades, evaluaciones y learning outcomes con los logros.
- Relaciona los logros con la credencial.
- Relaciona la credencial con el diploma.
- Guarda los ids creados en `src/data/advancedcredential/idlist.json` para reutilizarlos en ejecuciones posteriores.

Prerequisitos clave:
- Ids validos de issuing center, organization y diploma segun tu entorno (TEST/PRE/PRO).
- Acceso a la API con credenciales validas en `auth.json`.

### `test_advanced_credential_emission_tests.py`
Test de integracion que emite credenciales basadas en una plantilla ya creada.

Lo que hace:
- Autentica y obtiene el `credential_id` desde `src/data/advancedcredential/idlist.json`.
- Descarga la plantilla XLS de emision y la rellena con destinatarios.
- Divide el XLS en bloques (`emission_block_size`) y emite credenciales por bloque.
- Recupera el bloque de emisiones, sella las credenciales y espera hasta que queden selladas.
- Opcionalmente descarga JSON-LD y PDF de las credenciales selladas a `src/unittest/output_files` (si `downloadCredentials=true`).

Prerequisitos clave:
- Haber ejecutado antes el test de creacion para generar `idlist.json`.
- La plantilla y datos de emision existen en `src/data/advancedcredential/`.
- Credenciales y parametros correctos en `auth.json` y `params.json`.
