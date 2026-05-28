#----> Consideracion: Devuelve false de normal y devolvera true si no hay enzimas por las que se metaboliza con lo cual un break de manual <-------
#Cuando no hay enzimas por las que se metaboliza se tendrá en cuenta en si hay interacción o no?
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
        print("En esta web vamos a indicar si existe una interacción LEVE, MEDIA o ALTA basandonos en las enzimas por las que se metabolizan cada uno de los principios activos consultados en la base de datos de DrugBank")
        print()
        print("Solo se han tenido en cuenta las siguientes enzimas: [CYP2D6, CYP3A4, CYP3A5, CYP2C19, CYP2C9, CYP1A2] que según DrugBank son las 5 por las que se metabolizan mas principios activos. Teniendo en cuenta tambien la CYP3A5 que es como la CYP3A4 (CAMBIO), sin embargo cuando ambas mencionadas previamente se consideraban principales, la CYP3A5 era eliminada debido a  que la mayoria de la pobalcion no expresa esta enzima.")
        print()
        print()
        
    if len(enzimas) == 0:
        print(f"El principio activo: {ppio} no se metaboliza por ninguna enzima de las tenidas en cuenta según la base de datos de DrugBank, por tanto la interacción con cuaquier otro principio activo consultado aparecerá categorizada como LEVE")
        print()
    else:
        
        if len(enzimas) == 1:
            print(f"El principio activo: {ppio} solo se metaboliza por una enzima de las que se tienen en cuenta, la cual hemos considerado como enzima de metabolización principal del principio activo")
            #Aunque no tiene porque ser asi porque puede tener otra via principal de metabolizacion de enzimas no tenidas en cuenta, que pasaba con las fichas tecnicas de CIMA (salian otras enzimas de no mencionadas)
            print()
        else:
            
            if len(principales) == 0:
                print(f"El principio activo: {ppio} se metaboliza por las siguientes enzimas: {enzimas}, no se ha podido determinar la enzima principal por la que se metaboliza, por tanto las interacciones mostradas a continuacion serán con cada una de ellas")
                print()

            else:
                if len(principales) == 1:
                    print(f"El principio activo: {ppio} se metaboliza por las enzimas: {enzimas} de las cuales, se ha considerado principal: {principales}, en las siguientes descripciones se mostrarán las interacciones solo con dicha enzima considerada principal")
                    print()
                    
                else:

                    print(f"El principio activo: {ppio} se metaboliza por las enzimas: {enzimas}, de las cuales se han considerado principales las siguientes: {principales}, en las siguientes descripciones se mostrarán las interacciones solo con dichas enzimas consideradas principales")
                    print()









#SE MUESTRAN SOLO LAS INTERACCIONES EN LA PRIMERA INGESTA, PONER ESO
def texto_acciones (ppio_1, acc_1, ppio_2, acc_2, enzima):
    """
    Se describe la interaccion solo con la enzima concreta que se pasa por parámetro

    Parámetros
    --------------------
        ppio_1 -
        acc_1 -
        ppio_2 -
        acc_2 -
        enzima -
    Devolución
    --------------------
        None
    """

    #Declaramos cuales son las posibilidades
    posibilidades = ["inducer", "substrate", "inhibitor"]
    #Print explicativo
    print(f"En este caso solo se describen las interacciones de los principios activos con la enzima: {enzima} teniendo en cuenta solo que lleven a cabo algunas de las siguientes acciones: {posibilidades}")
    print()
    
    #De las listas proporcionadas con las acciones UNICAS eliminamos las que no tenemos en cuenta:
    mias_1 = [x for x in acc_1 if x in posibilidades]
    mias_2 = [x for x in acc_2 if x in posibilidades]

    #Guardamos una variable con las coincidencias de las acciones (sustrato-sustrato, inhib-inhib, induct-induct)
    #Se supone que ya deben de ser las distintas pero porsiacaso set
    doble = list(set(mias_1) & set(mias_2))

    #Una vez declaramos las variables comprobamos cada uno de los casos para obtener el texto adecuado
    #Aunque se ha comprobado que no hay elementos nulos en las acciones cuando la BBDD queda reducida a solo los que tienen enzimas se comprueba
    if (acc_1==None) or (acc_2==None):
        print(f"Las acciones de la enzima {enzima} para los principios activos {ppio_1} y {ppio_2} no están registradas en DrugBank, por tanto no se puede describir la interacción que tienen.")
        print()
        
    else:
        #De la lista ninguna es inductor-inhibidor-sustrato
        if (len(mias_1)==0) or (len(mias_2)==0):
            print(f"De las acciones que se llevan a cabo con la enzima: {e} en los dos principios activos consulltados: {ppio_1} y {ppio_2} ninguna es de las tenidas en cuenta, por tanto no se puede describir la interacción.")
            print()

        else:
            #Mostrar las posibilidades
            if doble:
                #Es posible que doble tenga mas de una acción ¿QUE HACES EN ESE CASO?
                print(f"")
                print()
            #Sustrato
            else:

            #PONER TEXTO GENERAL Y DICCIONARIO
                if "substrate" in acc_1:
                    
                    #sustrato-inductor
                    if "inducer" in acc_2:
                        print(f"Con la enzima: {e} el {ppio_1} está actuando como sustrato y {ppio_2} está actuando como inductor, en este caso tendría prevalencia el sustrato")
                        print()
                    #Se supone que con un else deberia valer
                    #sustrato-inhibidor
                    elif "inhibitor" in acc_2:
                        print(f"")
                        print()
    
                #Inhibidor
                elif "inhibitor" in acc_1:
                    
                    #inhibidor-indcutor
                    if "inducer" in acc_2:
                        print(f"")
                        print()
                    #Se supone que con un else deberia valer
                    #Inhibidor-sustrato
                    elif "substrate" in acc_2:
                        print(f"")
                        print()
    
                #Inductor (tambien podría ser solo un else en teoría)
                elif "inducer" in acc_1:
                    
                    #inductor-inhibidor
                    if "inhibitor" in acc_2:
                        print(f"")
                        print()
                    #Se supone que con un else deberia valer
                    #inductor-sustrato
                    elif "substrate" in acc_2:
                        print(f"")
                        print()





#Y NO SERÍA POSIBLE UN TEXTO GENERICO?? PARA LA ENZIMA E EL PPIO ACTIVO  1  ESTA ACTUANDO COMO: TRADUCCION DE SU ACTUACION Y EL DOS COMO: TRADD, EN ESTE CASO PREVALECERIA: (consulto diccionario con interacción?)

#Y SI UNO TIENE DOS ACCIONES????? CON QUE XUXA ME QUEDO