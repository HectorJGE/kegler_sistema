#!/bin/sh
PS3="Seleccionar una opcion de deploy "

select character in "Deploy latest" "Ingresar version (0.0.1)"
do
    if [[ $REPLY = 1 ]]
    then
        VERSION="latest"
    else
        echo -n "Enter the version: (0.0.1)"
        read VERSION
    fi

    # Build and push image
    docker build -f Dockerfile.prod . -t registry.gitlab.com/bellbird1/iribas/sistema:$VERSION
    docker push registry.gitlab.com/bellbird1/iribas/sistema:$VERSION

    # tag image
    git tag -a $VERSION -m "Version $VERSION"
    break
done