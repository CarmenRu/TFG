def texto_intro (ppio, enzimas, principales, primero=False):
    '''
    Texto de introducción de el principio activo concreto

    Parámetros
    ------------------------
        ppio - Principio activo que se va a describir
        enzimas - Lista con las enzimas por las que se metaboliza el ppio activo según la BBDD consultada
        principales - Lista con las enzimas principales (si las hay) por las que se metaboliza el ppio activo según las FT de CIMA con chat y notebook
        primero - Un booleano, por defecto en False que indica si es la primera vez que se ejecuta el texto o no para imprimir la introducción

    Devolución
    ---------------
        None
    '''
    if primero:
        print("En esta web vamos a indicar si existe una interacción LEVE, MEDIA o ALTA basandonos en las enzimas por las que se metabolizan cada uno de los principios activos consultados")
        print()
        print("Solo se han tenido en cuenta las siguientes enzimas: ["CYP2D6", "CYP3A4", "CYP3A5", "CYP2C19", "CYP2C9", "CYP1A2"] que según DrugBank son las 5 por las que se metabolizan mas principios activos. Teniendo en cuenta tambien la CYP3A5 que es como la CYP3A4 (CAMBIO), sin embargo cuando ambas mencionadas previamente se consideraban principales, la CYP3A5 era eliminada debido a  que la mayoria de la pobalcion no expresa esta enzima.")