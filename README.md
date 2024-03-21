# Sistema

Sistema de agendamientos, facturacion y administracion de la clinica de imagenes IRIBAS

## Docker :heart: Pycharm

Se recomienda seguir este tutorial para configurar correctamente el ide con docker.

<https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html>

## Iniciar el template

- Primero nos dirijimos a la carpeta startbootstrap-sb-admin-2
- Instalamos las dependencias npm `npm i`
- Compilamos las js css y vendors `npm run build`

Esto creara una carpeta dentro de `base\static` llamada `build`, en la misma se guardaran los archivos css, js, img,
y vendor compilados del template.

## Desarrollo de nuevos componentes

Para todos los componentes nuevos que se desarrollen a nivel de html, css y js que utilicen dependencias, se recomienda
el desarrollo grafico de los mismos en la carpeta del template para luego ser compilada y utilizada en el proyecto, para
tener una visualizacion del componente en formato demo y poder hacerle ajustes de usabilidad mas facilmente.

## Traducción del sistema

Para traducir los módulos, se ejecutan los siguientes comandos(un vez creadas las carpetas 'locale' en cada app):

- `django-admin makemessages -l es --ignore=site-packages` (donde 'es' se refiere al idioma español)<br>
  Este comando crea los archivos .po dentro de la carpeta locale de cada app,
  con las palabras que encuentre en el código, dentro de las funciones de traducción.<br>
  Ej: _('Name') <br>
  Al ejecutar este comando, en el archivo .po genera por ejemplo esto:<br>
  msgid "Name"<br>
  msgstr ""<br>
  Hay que escribir la traducción deseada en msgstr <br>
  ej:  
  msgid "Name"<br>
  msgstr "Nombre"<br>
  <br>
- `django-admin compilemessages` <br>
  Al ejecutar este comando se compila cada traducción para cada palabra, escrita en 'msgstr' del archivo .po.<br>
  Ojo: a veces el compiladar marcará como "Fuzzy" una traducción, lo que significa que esa palabra no será traducida, revisar ese detalle si una palabra no se está traduciendo.

## Carga de Datos de pruebas

Para cargar los datos de pruebas colocados en los distintos fixtures ejecutar loaddata <nombre del archivo del fixture sin la extención> ej: loaddata patients, para cargar datos de pruebas de los pacientes que se encuentran en el archivo patients.json.
Así tambien cada modulo posee un archivo <nombre del modulo>\_all.json donde se encuentran los datos de todos los modelos juntos.
El sistema tambien posee un archivo all.json que contiene los datos de todos los módulos juntos.

## Super User y Normal User

Entre los datos de pruebas se encuentran 2 usuarios, un super usuario de username "superuser", y un usuario "normaluser" los cuales su password se encuentra en el archivo de settings.py.

## Para correr con docker (Apple M1)

1. Correr docker login registry.gitlab.com/bellbird1/bellbird/sifen:latest para tener acceso a sifen con las credenciales de gitlab
2. correr `docker-compose -f docker-compose.local.yml up -d`
3. hacer `npm install node-sass@npm:sass` en startbootstrap y luego `npm i`
4. el devdependencie gulp-sass actualizar al 5.1.0
5. te va a decir que gulp-sass ya no tiene un sass por defecto y que tenes que marcar cual se va a usar
6. vas al startbootstrap-sb-admin-2/gulpfile.js y cambias  

```js
const sass = require('gulp-sass'); por
const sass = require('gulp-sass')(require('node-sass'));
```

1. luego npm run build
