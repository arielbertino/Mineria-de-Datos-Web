# -*- coding: utf-8 -*-
"""TP3_Mineria.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1snk51iiEFLzI--iHGH2DUMq90IOey5y5

TP3 - Minería de datos web

Descargar el siguiente dataset: 

http://www.cs.cornell.edu/people/pabo/movie-review-data/review_polarity.tar.gz

1. Escribir un Pipeline que permita clasificar las reviews de las películas como positivas o negativas.
2. Buscar una buena configuración de hiperparámetros para el clasificador elegido utilizando grid search.
3. Evaluar la performance del clasificador utilizando la técnica de hold out (75/25)
4. Evaluar la performance del clasificador utilizando validación cruzada.
5. Analizar los resultados obtenidos

Nota: para cargar documentos de texto con categorías, scikit-learn provee el método load_files(data_folder), que asume que dentro de "data_folder" hay una carpeta por cada clase posible, y dentro de esa carpeta se encuentran los documentos de texto plano

Aclaraciones del profe Marcelo:

En caso del dataset que les pasamos para este práctico, no está dividido previamente en dos partes como pasaba con el dataset que usé en clase (20 newsgroup). 

Entonces, para los puntos 1 y 2 del práctico, tienen que usar el dataset completo. En realidad, el grid search hace internamente cross validation para particionarlo. Con esta primera parte, tienen que elegir qué clasificador usar (luego de probar con 2 o 3 o más) y configurar los hiperparámetros que se adaptan mejor a los datos. 

Una vez que tienen seleccionado el clasificador que van a utilizar, de acuerdo a los resultados que obtuvieron hasta este punto, en los puntos 3 y 4 tienen que una partición explícita de los datos en prueba y entrenamiento usando dos de los métodos que vimos con este fin (hold hout en el punto 3, y cross validation en el punto 4)

Para analizar los resultados, usen al menos las tres métricas que vimos: precisión, recall y f-measure.
"""

# IMPORTACION DE LIBRERIAS
from sklearn import datasets
from pprint  import pprint
from sklearn.feature_extraction.text import CountVectorizer    
from sklearn.feature_extraction.text import TfidfTransformer   #TF-IDF
from sklearn.linear_model import LinearRegression              #Regresion Lineal
from sklearn.svm import SVC                                    #Maquina de vectores de soporte
from sklearn.linear_model import SGDClassifier                 #Clasificador estocastico de gradiente descendiente
from sklearn.naive_bayes import GaussianNB                     #Naive-Bayes Gaussiano
from sklearn.naive_bayes import MultinomialNB                  #Naive-Bayes Multinomial
from sklearn import neighbors                                  #KNN vecinos mas cercanos
from sklearn.pipeline import Pipeline                          #Mecanismo para Pipeline
from sklearn.model_selection import train_test_split           #Generador de cond de train y test
import numpy as np                                             #importo modulito que realiza operaciones varias
from sklearn.model_selection import GridSearchCV
import nltk
import time
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import StratifiedShuffleSplit

# defino algunos colores para imprimir mejor las cosas

negro    = '\u001b[30m'
rojo     = '\u001b[31m'
verde    = '\u001b[32m'
amarillo = '\u001b[33m'
azul     = '\u001b[34m'
magenta  = '\u001b[35m'
cyan     = '\u001b[36m'
blanco   = '\u001b[37m'
reset    = '\u001b[0m'

#comando para ejecutar entorno local
#jupyter notebook --NotebookApp.allow_origin='https://colab.research.google.com' --port=9090 --no-browser

"""En la siguiente celda de código se especifican 3 ruta al dataset solicitado por el enunciado, estas son "rutaExterna" (acceso publica a la carpeta drive propia), "ruta" (acceso desde al drive montado en el colab) y por ultimo "rutaLocal" (acceso a carpeta en pc local usada para procesar con kernel local).

Luego en "datos" se carga el dataset de acuerdo a la ubicación del mismo.
"""

rutaexterna = "https://drive.google.com/drive/folders/198RLXEf2wQRXsE0P76lnzTzUrolmCqJI?usp=sharing" #por si la quieren acceder desde afuera
ruta = "/content/drive/My Drive/Colab Notebooks/txt_sentoken"
rutaLocal = "/Users/Ariel/Desktop/txt_sentoken"
datos = datasets.load_files(rutaLocal)

"""A continución se realiza una limpieza previa de las reseñas del dataset, limpiando cosas como saltos de línea, espacios de mas antes de las comas, paréntesis entre otras cosas.

intenté limpiar un poco las reseñas pero luego cuando queria aplicar fit_transform(datosLimpios) me arrojaba incompatibilidad de tipo, ya que necesita un iterable sobre elemento de una lista de strings y datosLimpios resultaba siendo un string "plano", tampoco me dejaba castearlo a "sklearn.utils.Bunch".

Decidí dejar esta sección de códido para mostrar que intenté limpiar
un poco las reseñas pero no pude finalizar ese proceso. Al imprimir "datosLimpios" se puede observar la diferencia con "datos".
"""

# Alguna pruebas que fui haciendo

#datos                         # muestra los datos sin secuencias de escape, osea todo seguido 
#pprint(datos)                 # indica que el pretty print no se puede hacer ya que el notebook no soporta un IOstream tan grande
#clases = datos.target_names   # obtengo las clases del dataset
#print(clases)                 # Muestreo las clases
#print(type(datos))            # mostraba el tipo

datosLimpios = str(datos)
datosLimpios = datosLimpios.replace(". \\n","")
datosLimpios = datosLimpios.replace(" , ",", ")
datosLimpios = datosLimpios.replace("\\n","")
datosLimpios = datosLimpios.replace("\\s","")
datosLimpios = datosLimpios.replace("\\'","'")
datosLimpios = datosLimpios.replace("\'","'")
datosLimpios = datosLimpios.replace("( ","(")
datosLimpios = datosLimpios.replace(" )",")")

#print(type(datosLimpios))     # Muestra el tipo de la varible que terminé descartando "datosLimpios"
#print(datosLimpios)           # Muestra el contenido "pulido" del dataset, igualmente no la usé por lo explicado más arriba

"""Definí un vectorizador y un transformador TF-IDF para hacer pruebas y observa resultados"""

#Vectorizador

vectorizador = CountVectorizer()
vecDatos = vectorizador.fit_transform(datos.data) 
#print(vectores.shape)        # muestra estructura (nroDocs, CantDeTokens)
#print(vectores[0])      # muestra (EnDocTal, ElTokenTal)   ApareceCantVeces  #estructura de la salida

#TF-IDF

transformadorTFIDF = TfidfTransformer()
tfidfDatos = transformadorTFIDF.fit_transform(vecDatos)

"""A partir de este punto empiezo a definir diferentes clasificadores con el objetivo de observar el comportamiento através de los mismos en su versión "más estandar" (sin modificar ningun hiperparámetro) """

# Ver que hiperparámetros tiene cada clasificador
# Lo deje comentado por que cuando queria imprimir los paramentro con kernel local no me mostraba los parametros

maqVectSoporte  = SVC()
mVSEstoGradDesc = SGDClassifier()
nbGaussiano     = GaussianNB()
nbMultinomial   = MultinomialNB()
vecinosMasCerca = neighbors.KNeighborsClassifier()

#maqVectSoporte.get_params()
#mVSEstoGradDesc.get_params()
#nbMultinomial.get_params()
#vecinosMasCerca.get_params()

# Maquina de vector de soporte (SVC):

# SVC('C': 1.0,'break_ties': False, 'cache_size': 200,
#    'class_weight': None, 'coef0': 0.0, 'decision_function_shape': 'ovr', 
#    'degree': 3, 'gamma': 'scale', 'kernel': 'rbf', 'max_iter': -1, 
#    'probability': False, 'random_state': None, 'shrinking': True, 
#    'tol': 0.001, 'verbose': False)

# SVC Estocástico de gradiente descendente: 

# SGDClassifier(alpha=0.0001, average=False, class_weight=None,
#              early_stopping=False, epsilon=0.1, eta0=0.0, fit_intercept=True,
#              l1_ratio=0.15, learning_rate='optimal', loss='hinge',
#              max_iter=1000, n_iter_no_change=5, n_jobs=None, penalty='l2',
#              power_t=0.5, random_state=None, shuffle=True, tol=0.001,
#              validation_fraction=0.1, verbose=0, warm_start=False)

# Naive-Bayes Multinomial

# MultinomialNB(alpha=1.0, class_prior=None, fit_prior=True)

# Vecinos mas cercanos

# KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski',
#                    metric_params=None, n_jobs=None, n_neighbors=5, p=2,
#                    weights='uniform')

"""Defino varios pipelines que usaré en la función "oraculoDeDelfos" para predecir las clases de las reseñas (documentos-ejemplos). 

Comenté el pipeline con el clasificados Naive-bayes gaussiano ya que como trabaja con datos continuos pedia convertir los detos a una matriz densa. Decidí omitir su uso ya que los datos que se usan en este trabajo con discretos, así como también el uso de un método de regresión lineal, ya que arrojaba resultados demasiado dispares comparado con otros métodos.

En la siguiente celda de código se realizan pruebas con los clasificadores, "por defecto", no se le modificó ningun hiperparámetro, esta tarea de realizará más adelante, utilizando gridSearch (busqueda exahustiva de hiperparámetros).
"""

# definición de clasificadores, verbose=True hace que se muetre el tiempo invertido en cada paso del pipeline dado
# A la hora te probar este codigo, descomentar el parametro verbose=True asi en la sadia se podrá apreciar el tiempo
# de cada paso del pipeline, lo comenté ya que a la hora de hacer gridSearch me mostraba muchos detos debido la cantidad
# de combinaciones que probaba
clasificadorMVS = Pipeline([ ('VEC', CountVectorizer()), ('TFIDF', TfidfTransformer()), ('CLAS', SVC())], """verbose=True""")
clasificadorEGD = Pipeline([ ('VEC', CountVectorizer()), ('TFIDF', TfidfTransformer()), ('CLAS', SGDClassifier())], """verbose=True""")
clasificadorNBM = Pipeline([ ('VEC', CountVectorizer()), ('TFIDF', TfidfTransformer()), ('CLAS', MultinomialNB())], """verbose=True""")
clasificadorKNN = Pipeline([ ('VEC', CountVectorizer()), ('TFIDF', TfidfTransformer()), ('CLAS', neighbors.KNeighborsClassifier())], """verbose=True""")
#clasificadorNVG = Pipeline([ ('VECTORIZADOR', CountVectorizer()), ('TFIDF', TfidfTransformer()), ('CLASIFICADOR', GaussianNB())  ])

print(magenta+"Clases reales:    ", datos.target,""+reset)

def oraculoDeDelfos(clasi, dat):
  print(negro+"--------------------------------------------------------------------------------------------------------------------------------"+reset)
  print(azul+"Pipeline usado: ",clasi.named_steps,""+reset)                                       #named_steps muestra los pasos que tiene el clasificador
  print(amarillo+"Tiempo invertido en cada paso del pipeline:"+reset)
  p = clasi.fit(dat.data, dat.target)
  predecido = p.predict(dat.data)
  mediaDeAcierto = "{0:.3f}".format(np.mean(predecido == dat.target) * 100)                #format me permite mostrar una cantidad de decimales dada
  print(rojo+"Clases obtenidas:",predecido, ", Porcentaje de exito:", mediaDeAcierto, "%"+reset)
  print(negro+"--------------------------------------------------------------------------------------------------------------------------------"+reset)

 
# las siguientes lineas tardan en ejecutarse entre 30 y 45 segundos 
# en un procesador intel i7 de 2.6 GHz con 4 Nucles y 16GB de ram

# pido la ayuda del
oraculoDeDelfos(clasificadorMVS, datos)
oraculoDeDelfos(clasificadorEGD, datos)
oraculoDeDelfos(clasificadorNBM, datos)
oraculoDeDelfos(clasificadorKNN, datos)
#oraculoDeDelfos(clasificadorNVG, datos)

"""Se puede observar en los resultados anteriores se puede observar que el orden de mayor a menos acierto entre las clases reales y las clases predecidas en porcentaje son: 

---
|Clasificador|Porcentaje acierto|  
|--------------------------|----|
|SVM SGD                   |100 |
|SVM                       |99.8|
|NB Multinomial            |95.7|
|KNN                       |69.3|

---

Se puede observar como el tiempo para vectorizar y para TF-IDF es aproximandamete el mismo en todos los pipelines (ya que son los mismo para todos), pero cambia sustancialemte en tiempo de la predicción con la máquina de vectores de soporte ya que tiene que recorrer todos los documentos previos para clasificar un documento nuevo.

También cabe aclarar que tanto los conjuntos de entrenamiento y prueba son los mismos (el dataset completo), con lo cual se esperaría que el procentaje de acierto en las prediciones fuese alto (esto se ve con SVM-SGD, SVM y en NB-Multinomial). Esto se debe a que el modelo se sobreentrenó(overfiting), con lo cual el modelo esta muy centrado en los datos de entrenamiento y el ser iguales a los de prueba arroja una taza de acierto alta. A la hora de clasificar nuevos documentos posiblemente arroje errores donde no lo sea.

Pero es relativamente bajo el porcenteje de error al usar KNN(vecinos mas cercanos). Esto se debe a la naturaleza intrínseca de propio algorítmo, donde cada documento es un punto en el espacio y se compara los documentos en el espacio con el documento a ser clasificado. Esto generará un bajo nivel de acierto ya que la clasificación se basa en los vecino más cercanos que tenga ese nuevo documento.

Desde aquÍ se particiona arbitrariamente el dataset inicial para un 75% de entretamiento y un 25% de prueba, con el fin de desarrollar los incisos 3 y 4 del enunciado. Además se tendrá en cuenta la estimación de parámetros con el fin de aumentar la taza de aciertos entre otras métricas usadas en el desarrollo
"""

# "train_test_split" puede tener un parámetro shuffle=True que mezclará 
# el dataset antes de dividir en conjuntos de entrenamiento y prueba
# "train_test_split" es un métpdp de holdout

datosEntrenamiento, datosPrueba, clasesRealesDEntre,clasesRealesDPrueba = train_test_split(datos.data, datos.target, test_size=0.25)
#print(datosPrueba)

#Defino vectoridor y tranformador TF*IDF para drigSearch

vectorInfo = vectorizador.fit_transform(datosEntrenamiento) 
tfidfInfo = transformadorTFIDF.fit_transform(vectorInfo)

def encontrarLoMejor(pipeline, parametros, datosTrain, clasesTrain): 
  print(negro+"---------------------------------------------------------------------------------------------------------------------------------------------------------"+reset)
  print(amarillo+"Pipeline usado: ",pipeline.named_steps,""+reset)
  g = GridSearchCV(pipeline, parametros, cv=5, n_jobs=-1)
  g = g.fit(datosTrain, clasesTrain)
  print(azul+"La mejor taza de acierto fue de:", "{0:.4f}".format(g.best_score_ * 100),""+reset)
  print(rojo+"Con los siguientes voleres de parámetros:"+reset)
  print(rojo+"",g.best_params_,""+reset)
  print(negro+"---------------------------------------------------------------------------------------------------------------------------------------------------------"+reset)

# Defino la lista de parametro para cada clasificador

parametrosMVS = {'VEC__ngram_range':[(1,1),(1,2)], 'VEC__stop_words': ['english'],'TFIDF__use_idf': [True,False], 'CLAS__kernel': ['linear','poly','rfb','sigmoid'], 
                 'CLAS__coef0': [1e-2, 1e-3], 'CLAS__C':[1.0, 2.0]}    
parametrosEGD = {'VEC__ngram_range':[(1,1),(1,2),(1,3)], 'VEC__stop_words': ['english'], 'TFIDF__use_idf': [True,False], 'CLAS__alpha': [1e-2, 1e-3, 1e-4]}
parametrosNBM = {'VEC__ngram_range':[(1,1),(1,2),(1,3)], 'VEC__stop_words': ['english'], 'TFIDF__use_idf': [True,False], 'CLAS__alpha': [1e-2, 1e-3, 1e-4]}
parametrosKNN = {'VEC__ngram_range':[(1,1),(1,2)], 'VEC__stop_words': ['english'], 'TFIDF__use_idf': [True,False], 'CLAS__leaf_size': [15, 30, 45], 
                 'CLAS__n_neighbors': [2, 5, 8]}

# las siguientes lineas tardan en ejecutarse entre 7 y 8,5 minutos 
# en un procesador intel i7 de 2.6 GHz con 4 Nucles y 16GB de ram

encontrarLoMejor(clasificadorMVS, parametrosMVS, datosEntrenamiento, clasesRealesDEntre)  
encontrarLoMejor(clasificadorEGD, parametrosEGD, datosEntrenamiento, clasesRealesDEntre)  
encontrarLoMejor(clasificadorNBM, parametrosNBM, datosEntrenamiento, clasesRealesDEntre)  
encontrarLoMejor(clasificadorKNN, parametrosKNN, datosEntrenamiento, clasesRealesDEntre)

"""Antes de presentar la información de las mediciones, se debe aclarar que se parcionó el dataset original en particiones 75/25 para los conjuntos de entrenamiento y de prueba respectivamente. Tambien se volvían a calcular entre prueba y prueba para para tener un panorama más amplio de a situacion

Mediate la aplicación de los métodos anteriores, obtuve con una taza de acierto de entre aproximadamente 82.7 % y 84.6 % al usar el el clasificador SVC (maquina de vectors de soporte). A continuación la los valores de la última prueba realizada:

**Pipeline usado**:  
{'VEC': CountVectorizer(), 'TFIDF': TfidfTransformer(), 'CLAS': SVC()} 

**La mejor taza de acierto fue de:** 84.6000 

C**on los siguientes voleres de parámetros:**

 {'CLAS__C': 2.0, 'CLAS__coef0': 0.01, 'CLAS__kernel': 'linear', 'TFIDF__use_idf': False, 'VEC__ngram_range': (1, 1), 'VEC__stop_words': 'english'} 

 Por otro lado el clasificador que menor taza da acierto arrojaba en todas las pruebas fue el KNN(vecinos más cercanos)

Para continuar con el análisis de los datos procederemos a realizar y/o calcular:

> **Matriz de confusión**: Matriz que dispone los verdaderos positivos y verdaderos negativos(aciertos) en su diagonal y tambien el resto po por ejemplo los falsos negativos y los falsos positivos. con esta información se puede calcular distintas métricas con el fin de analisar que tan bine funciona un clasificador

> **Holdout**: Es un técnica para dividir los datos iniciales(o no), en un 
conjunto de entrenamiento y otro de prueba

> **Validación cruzada**:

> **Precisión**:  Indica, de las veces que se predijo de una clase, cuantas fueron correctas

> **Recall:** intenta medir si yo puede identificar todos los documento pertecientes a una clase

> **F-measure**: Es una media armónica entre preción y recall. Indica una medida de calidad más general del modelo(clasificodor) utilizado.
"""

# Antes que nada estableceremos una particion del dataset para poder 
# opretar con los datos, aclarando que estas particones serán distintas 
# en cada ejecución, cabe aclarar que en la siguiente linea, se está
# utilizada una tecnica de particionamiento de datos llamada holdout
# atravéz de la funci;o train_test_split(...)

datosEntrenamiento, datosPrueba, clasesRealesDEntre,clasesRealesDPrueba = train_test_split(datos.data, datos.target, test_size=0.25)

# Construccion de la matriz de confusión

# Defino un clasificador con los hiperparámetros obtenidos anteriormente
clasificadorDefinitivo = Pipeline([ ('VEC', CountVectorizer(ngram_range=(1,1), stop_words= 'english')), ('TFIDF', TfidfTransformer(use_idf=False)), 
                          ('CLAS', SVC(C=2.0, coef0=1e-2, kernel='linear'))])
clasificadorDefinitivo = clasificadorDefinitivo.fit(datosEntrenamiento, clasesRealesDEntre)  #entrenamiento
predicho = clasificadorDefinitivo.predict(datosPrueba)                                       #predicción

# Defino la matriz de confución
matrizConfusion = confusion_matrix(clasesRealesDPrueba, predicho)
print(azul+"Matriz de confusión que resulta proviene de"+reset)
print(azul+"las clases reales del conjunto de prueba y de"+reset)
print(azul+"las clases predichas del conjunto de prueba")
print(azul,matrizConfusion)

"""La matriza de confusión nos está indicando que la maxima concentración de ejemplos se encuentras en la diagonal principal, esta es un claro indicativos de que el claficidor utilizado junto con los hiperparámetros encontrados predicen con gran preción los verdaderos positivos y los verdaderos negativos. 

Esta informacion es muy buena, pero también un factor que influye es el hecho de que no una gran cantidad de clases para clasificar, sumado al hecho de que ambas clases inicialmente parecerían estar representadas por números no tan distantes entre sí de ejemplos.
"""

# Muestro distintas métricas

clases = ['Negativas', 'Positivas']
print(classification_report(clasesRealesDPrueba, predicho, target_names=clases))

"""De las métricas anteriores se puede observar con claridad que preción de las predicciones de las clases negativa y positiva es de un 85% y 80% respectivamente es nos lleva a buen puerto ya que nos indica que el clasificador utilizado cumple con esos porcentajes de acierto el acto de clasificar un documento como posivo y como negativo cuando realmente esos documentos si correspondían a dichas clases.

En forma analoga en recall de ambas clases nos dice que del total de negativos y de positivos(documento, en este caso reseñas), respectivamente el 77 % y el 86 %  fueron correctamente clasificados. Donde si bien la cantidad de positivas del totas el del 77% nos deja tranquilos saber que del total de negativas el 86% fueron correctamente clasificados como negativos. Estos resultados son más que acptable en el contexto de trabajo(reseñas de cine).

Por ultima y para tener un acercamiento al rendimiento global del clasificador tanto el macroPromedio como el promedioPesado aroojaron un 82% de confiabilidad en el claficados

>*  Como último paso de todo este análisis realizaremos lo que llama validación cruzada, con el fin de obtener un número mas representativo de cual es la eficiencia del clasificador. Esto se logra tomando en conjunto de datos y particionandoo en N conjuntos disjuntos donde se realiza N pruebas con N-1 conjuntos para estrenamiento y uno para prueba, se calculan N puntajes y se los promedio obteniendo un valor mas certero para un modelo dado.
"""

# Se define un ventorizador, un clasificador y se los usa
# para generar el vector de puntajes, esta tarea la rfealizo
# Para cada uno de los distintos metodos de validacion cruzada

vect = TfidfVectorizer(stop_words='english',ngram_range=(1,1) )
vect = vect.fit_transform(datos.data)
clf = SVC(C=2.0, coef0=1e-2, kernel='linear')
clas=datos.target

#dDefino varios validadores
cv_comun = 5
cv_kfold = KFold(n_splits=5)
cv_strat = StratifiedKFold(n_splits=5)
cv_suffle = ShuffleSplit(n_splits=5)
cv_suffle_strat = StratifiedShuffleSplit(n_splits=5)

def obtenerScores(validacion):
  print(negro+"---------------------------------------------------------------------------------------------------------------------------------------------------------"+reset)
   puntaje=cross_val_score(clf, vect, clas,cv=validacion,n_jobs=-1)
  print(rojo+"Vector de puntajes(scores), con cv =",validacion,":",puntaje,reset)
  print(azul+"Se obtuvo una exactitud media de:","{0:.4f}".format(puntaje.mean()),", con un margen de error de +/-", "{0:.4f}".format(puntaje.std()*2)+reset)
  print(negro+"---------------------------------------------------------------------------------------------------------------------------------------------------------"+reset)

# las siguientes lineas tardan en ejecutarse entre 45 segundos y 1 minutos 
# en un procesador intel i7 de 2.6 GHz con 4 Nucles y 16GB de ram

print(amarillo+"Se mostrará la métrica exactitud para varios tipos de validación cruzada: "+reset)
obtenerScores(cv_comun)
obtenerScores(cv_kfold)
obtenerScores(cv_strat)
obtenerScores(cv_suffle)
obtenerScores(cv_suffle_strat)

"""Para concluir el análisis, primero remarco algunos detalles como que para todas las validaciones cruzadas se utlizó el clasificador que se obtuvo a la hora de compara distintos tipo de claificadores, donde elejí usar una maquina de vectores de soporte, aplicando remoción de stopwords basado un diccinario de stopwords etandar del ingles, basadose en el reconocimiento de token simple(1-gramas) entre otros atributos. Luegos este clasficador mismo que se usé para las diferentes tecnicas de validación cruzada.

En lo que refiere a validacion cruzada se midió el desempeño de los siguiente métodos: estandar(donde se define un valore de cv=5 para este caso), Kfold, Kfold estratificado, división aleatoria y división aleatoria estratificada. Resultando la división aleatoria con mayor exactitud media pero tambien con un mayor margen de error donde los valores ascilarian en un rango más amplio. Por el lado opuesto se obtuvo a KfoldEstratificado con menor exactitud promedia y margen de error, si bien es menor posee menos variabilidad que división aleatoria.

Dependiendo el domino de aplicación podría se más ventajo optar por una tecnica u otra. En este dominio puntual(reseñas de peliculas), no es significante, con lo cual cualquier método esta más que correcto para clasificar.

Detalle: los métodos de validación cruzada se puede aplicar sobre cualquier metrica que uno desee con el fin de maximizarla o minimizarla, en este casa sobre exactitud.
"""