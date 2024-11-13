# -*- coding: utf-8 -*-
"""Tarea Modelos_de_Ensamble_Ejercicio_Milko R.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Zj89CuH3KH8cMyKLYT4LKXBPZG9gg3BK

# Ejercicio en clase: Modelos de Ensamble

Este ejercicio tiene como objetivos:

* Aprender a entrenar modelos de ensamble por Votación y Random Forests
* Consolidar el conocimiento del proceso de preparación, ajuste y evaluación de modelos predictivos
* Practicar la optimización de hiperparámetros usando búsqueda aleatoria y búsqueda en grilla
* Visualizar las características más importantes identificadas por Random Forests

# Ensamble por votación manual

## Ejemplo de `scikit-learn`

Como inicio de este ejercicio tomemos una ilustración de la documentación de `scikit-learn`: [Plot the decision boundaries of a VotingClassifier](http://scikit-learn.org/stable/auto_examples/ensemble/plot_voting_decision_regions.html). En ella se diagrama las fronteras de decisión de un modelo de ensamble por votación, usando dos de las cuatro características del [Iris Flower Data Set](https://en.wikipedia.org/wiki/Iris_flower_data_set): largo del sépalo y largo del pétalo.

El conjunto de datos Iris contiene 50 muestras de cada una de tres posibles especies de Iris: *Iris setosa, Iris virginica* e *Iris versicolor*. Para cada muestra se tiene la medida en centímetros de cuatro características: largo y ancho de los pétalos y de los sépalos.

Este modelo por ensamble combina por votación las probabilidades de clase asignadas por tres clasificadores de base: un árbol de decisión (`DecisionTreeClassifier`), un modelo k-NN (`KNeighborsClassifier`), y una máquina de soporte vectorial con kernel gaussiano (`SVC`).

Se ha asignado manualmente a los modelos los pesos `[2, 1, 2]`, lo que significa que, al promediar las probabilidades obtenidas de los modelos, las probabilidades del árbol de decisión y de la máquina de soporte vectorial cuentan el doble que las del modelo k-NN.
"""

# Commented out IPython magic to ensure Python compatibility.
# Tomado de http://scikit-learn.org/stable/auto_examples/ensemble/plot_voting_decision_regions.html

from itertools import product

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
# %matplotlib inline

from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import VotingClassifier


# Loading some example data
iris = datasets.load_iris()
X = iris.data[:, [0, 2]]
y = iris.target

# Training classifiers
clf1 = DecisionTreeClassifier(max_depth=4)
clf2 = KNeighborsClassifier(n_neighbors=7)
clf3 = SVC(gamma=.1, kernel='rbf', probability=True)
eclf = VotingClassifier(estimators=[('dt', clf1), ('knn', clf2),
                                    ('svc', clf3)],
                        voting='soft', weights=[2, 1, 2])

clf1.fit(X, y)
clf2.fit(X, y)
clf3.fit(X, y)
eclf.fit(X, y)

# Plotting decision regions
x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.1),
                     np.arange(y_min, y_max, 0.1))

f, axarr = plt.subplots(2, 2, sharex='col', sharey='row', figsize=(10, 8))

for idx, clf, tt in zip(product([0, 1], [0, 1]),
                        [clf1, clf2, clf3, eclf],
                        ['Decision Tree (depth=4)', 'KNN (k=7)',
                         'Kernel SVM', 'Soft Voting']):

    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    axarr[idx[0], idx[1]].contourf(xx, yy, Z, alpha=0.4)
    axarr[idx[0], idx[1]].scatter(X[:, 0], X[:, 1], c=y, alpha=0.8)
    axarr[idx[0], idx[1]].set_title(tt)

plt.show()

# Ver las probabilidades asignadas por KNN (k=7) a cada clase en cada uno de los últimos 5 ejemplos del conjunto de entrenamiento
print(clf2.predict_proba(X[-5:]))

"""## Evaluación del modelo de ensamble por votación manual

Observemos la exactitud *(accuracy)* de cada uno los modelos:
"""

print ("Exactitud del modelo de árbol de decisión     :", clf1.score(X, y))
print ("Exactitud del modelo de k-NN                  :", clf2.score(X, y))
print ("Exactitud del modelo SVM de kernel gaussiano  :", clf3.score(X, y))
print ("Exactitud del modelo de ensamble por votación :", eclf.score(X, y))

"""¿A qué crees que se debe que en este caso no se haya llegado a un 100% de exactitud? (sesgo, varianza, error irreducible)

Dado que los modelos anteriores han sido entrenados en la totalidad de instancias del conjunto de datos Iris, ¿se puede decir que los valores anteriores son buenos indicadores del rendimiento que se tendrá fuera de la muestra (p.ej. en un conjunto de pruebas)?

# Ensamble por Bagging con Random Forests

En esta parte del ejercicio usaremos el conjunto de datos [Titanic: Machine Learning from Disaster](https://www.kaggle.com/c/titanic). A partir de un conjunto de características sobre cada pasajero se requiere predecir si sobrevivió o no a la tragedia. Ver la [descripción de los datos](https://www.kaggle.com/c/titanic/data)

En los siguientes pasos tenemos un ejemplo básico del proceso típico de aprendizaje de modelos predictivos.

## Obtención y carga de datos
"""

titanic_train = pd.read_csv('train.csv')
titanic_test = pd.read_csv('test.csv')
titanic_train.head()

titanic_test.head()

"""## Algunas visualizaciones"""

sns.catplot(x="Sex", y="Survived", hue="Pclass", kind="bar", data=titanic_train);

sns.pairplot(titanic_train, hue="Survived");

"""## Preparación de los datos

`Pandas` nos permite seleccionar una columna como índice. En nuestro caso el índice es conveniente hacer con la columna `PassengerId`.
"""

titanic_train.set_index('PassengerId', inplace=True)
titanic_test.set_index('PassengerId', inplace=True)
titanic_train.head()

"""### Lidiando con los valores faltantes

Usando un simple conteo en el conjunto de entrenamiento, podemos verificar que falta algunos valores para `Embarked`, `Age` y sobre todo `Cabin`.
"""

titanic_train.count()

"""En el conjunto de prueba, vemos que falta también un dato en `Fare`:"""

titanic_test.count()

"""Hay diversas maneras de lidiar con valores faltantes. En este ejercicio haremos las siguientes opciones:

* `Embarked`: Sólo falta dos valores en el conjunto de entrenamiento. Imputaremos la moda (valor más frecuente).
"""

# Sólo hay dos valores faltantes NaN. La moda (valor más frecuente) es 'S'
titanic_train['Embarked'].value_counts(dropna=False)

# Registramos el índice (PassengerId) de los dos casos, y luego mostramos ambos registros
embarked_NaN = titanic_train[titanic_train['Embarked'].isnull()].index
print('Los PassengerId en los que falta Embarked son: ', embarked_NaN.values)

titanic_train.loc[embarked_NaN]

# Calculamos la moda
embarked_moda = titanic_train['Embarked'].mode()[0]
print("La moda (valor más frecuente) de Embarked en el conjunto de entrenamiento es: ", embarked_moda)

# Imputamos la moda en los valores faltantes
titanic_train.loc[embarked_NaN,'Embarked'] = embarked_moda
titanic_train.loc[embarked_NaN]

"""![texto alternativo](https://)* `Age`: Incluiremos un campo booleano de `EdadDesconocida` y adicionalmente completaremos el valor con la mediana."""

# Creamos una columna para caracterizar los casos con edad desconocida
titanic_train['EdadDesconocida'] = titanic_train['Age'].isnull()
titanic_test['EdadDesconocida'] = titanic_test['Age'].isnull()

# Calculamos la mediana de Age y la imputamos en los valores faltantes de ambos conjuntos
# Mostramos cómo hacerlo con DataFrame.fillna()
age_mediana = titanic_train['Age'].median()
print("La mediana del campo Age en el conjunto de entrenamiento es: ", age_mediana)

titanic_train['Age'].fillna(age_mediana, inplace=True)
titanic_test['Age'].fillna(age_mediana, inplace=True)

"""* `Fare`: Un solo caso, en el conjunto de prueba. Imputaremos la mediana del conjunto de entrenamiento."""

fare_mediana = titanic_train['Fare'].median()
print("La mediana del campo Fare en el conjunto de entrenamiento es: ", fare_mediana)

titanic_test['Fare'].fillna(fare_mediana, inplace=True)

"""* `Cabin`: No usaremos la clase `Cabin`, severamente incompleta."""

titanic_train.drop(['Cabin'], axis=1, inplace=True)
titanic_test.drop(['Cabin'], axis=1, inplace=True)

"""### Selección de características

Ya hemos retirado la columna `Cabin`, severamente incompleta. Retiraremos también `Name` y `Ticket`, por ser campos irrelevantes para efectos de la predicción.
"""

titanic_train.drop(['Name','Ticket'], axis=1, inplace=True)
titanic_test.drop(['Name','Ticket'], axis=1, inplace=True)

"""Podemos añadir otras meta-características. Por ejemplo, podríamos crear una columna `ViajaSolo` cuando no el pasajero no viajó  con ningún familiar: 0 `SibSp` (viaja con hermanos o cónyuge) y 0 `Parch` (viaja con padres o hijos)."""

titanic_train['ViajaSolo'] = ((titanic_train['SibSp'] + titanic_train['Parch']) == 0)
titanic_test['ViajaSolo'] = ((titanic_test['SibSp'] + titanic_test['Parch']) == 0)
titanic_train.head()

titanic_test.head()

"""Añade las columnas `MenorDeEdad` y `AdultoMayor`. Considera como menor de edad a todos aquellos menores de 18.0 años. Considera Adulto Mayor a los mayores de 55.0 años. Hazlo tanto en el conjunto de entrenamiento como en el de pruebas."""

## COMPLETAR
titanic_train['MenorDeEdad'] = (titanic_train['Age'] < 18.0)
titanic_test['MenorDeEdad'] = (titanic_test['Age'] < 18.0)

titanic_train['AdultoMayor'] = (titanic_train['Age'] > 55.0)
titanic_test['AdultoMayor'] = (titanic_test['Age'] > 55.0)

# Creando la columna 'MenorDeEdad'
titanic_train['MenorDeEdad'] = titanic_train['Age'] < 18.0
titanic_test['MenorDeEdad'] = titanic_test['Age'] < 18.0

# Creando la columna 'AdultoMayor'
titanic_train['AdultoMayor'] = titanic_train['Age'] > 55.0
titanic_test['AdultoMayor'] = titanic_test['Age'] > 55.0

print(titanic_train[['Age', 'MenorDeEdad', 'AdultoMayor']].head())
print(titanic_test[['Age', 'MenorDeEdad', 'AdultoMayor']].head())

"""**Pregunta 3:** ¿Cuántos menores de edad hay en el conjunto de entrenamiento?"""

menores_de_edad = titanic_train['MenorDeEdad'].sum()
print(f"Número de menores de edad en el conjunto de entrenamiento: {menores_de_edad}")

"""**Pregunta 4:** ¿Cuántos adultos mayores hay en el conjunto de pruebas?"""

# Contar adultos mayores en el conjunto de pruebas
adultos_mayores_pruebas = titanic_test['AdultoMayor'].sum()
print(f"Número de adultos mayores en el conjunto de pruebas: {adultos_mayores_pruebas}")

"""### Codificación de variables categóricas

Tenemos también tres variables categóricas (`Sex`, `Pclass` y `Embarked`). Las convertiremos en datos numéricos para que facilitar su entrenamiento por cualquier modelo.

* `Sex`: la podemos reemplazar por un valor binario `EsMujer` (0 = hombre; 1 = mujer).
"""

titanic_train['EsMujer'] = (titanic_train['Sex'] == 'female')
titanic_test['EsMujer'] = (titanic_test['Sex'] == 'female')

titanic_train.drop(['Sex'], axis=1, inplace=True)
titanic_test.drop(['Sex'], axis=1, inplace=True)

"""* `Pclass` y `Embarked`: Usaremos *one-hot encoding* con la función `DataFrame.get_dummies` de `pandas`.

  `Pclass` es la clase en la que viajó el pasajero (1 = primera clase; 2 = segunda clase; 3 = tercera clase).

  `Embarked` es el puerto de embarque (C = Cherbourg; Q = Queenstown; S = Southampton).

  Observa que `Pclass` es categórica no obstante haya sido representada con una codificación numérica.
"""

cols_categoricas = ['Pclass','Embarked']

titanic_train = pd.get_dummies(titanic_train, columns=cols_categoricas)
titanic_test = pd.get_dummies(titanic_test, columns=cols_categoricas)

titanic_train.head()

titanic_test.head()

"""## Separación de conjunto para validación"""

from sklearn.model_selection import train_test_split

X_train_val = titanic_train.drop('Survived', axis=1)
y_train_val = titanic_train['Survived']

X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.2, random_state=0)

"""## Entrenamiento de Random Forests

Probemos primero entrenando un modelo Random Forest con los parámetros que trae por defecto.
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

rf = RandomForestClassifier(oob_score = True)
rf.fit(X_train, y_train)

print('Exactitud del modelo inicial en entrenamiento:', rf.score(X_train, y_train))
print('Exactitud del modelo inicial en entrenamiento (Out of Bag):', rf.oob_score_)
print('Exactitud del modelo inicial en validación:', rf.score(X_val, y_val))

"""### Búsqueda aleatoria de hiperparámetros

El clasificador de Random Forest tiene diversos parámetros que pueden ser optimizados. Se puede ver la documentación de [sklearn.ensemble.RandomForestClassifier](http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)

Los principales hiperparámetros de Random Forest son:
- `n_estimators` -- el número de modelos base (árboles) a entrenar
- `max_features` -- el número de características a considerar en cada partición de los árboles
- `max_depth` -- la profundidad máxima de los árboles
- `min_samples_leaf` -- el numero mínimo de muestras que deben quedar en cada hoja del árbol

Para identificar los mejores valores de los hiperparámetros usaremos primero búsqueda aleatoria y luego búsqueda en grilla.
"""

from pprint import pprint

n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
max_features = ['auto', 8, 10, 12, None]  # 'auto' equivale a 'sqrt'; None equivale a todas las 15
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)] + [None]
min_samples_leaf = [1, 2, 4]

random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_leaf': min_samples_leaf}

print('Los valores a probar en la búsqueda aleatoria son:')
pprint(random_grid)

print()
print('Si se probara todas las combinaciones se requeriría entrenar',
      len(random_grid['n_estimators']) *
      len(random_grid['max_features']) *
      len(random_grid['max_depth']) *
      len(random_grid['min_samples_leaf']),
      'modelos'
      )

"""Probaremos entrenando sólo un 2% de las combinaciones posibles, es decir, 18. (Se recomienda probar al menos un 10%)"""

from sklearn.model_selection import RandomizedSearchCV

rf = RandomForestClassifier(oob_score=True)
rf_random = RandomizedSearchCV(estimator = rf,
                               param_distributions = random_grid,
                               n_iter = 18,
                               cv = 3,          # Validación cruzada 3-fold
                               verbose=2,
                               random_state=0,
                               n_jobs = -1      # Paralelizar en todos los cores disponibles
                               )
rf_random.fit(X_train, y_train)

rf_random_best = rf_random.best_estimator_

print('Los hiperparámetros del mejor modelo son:')
pprint(rf_random.best_params_)
print()

print('Exactitud luego de búsqueda aleatoria en entrenamiento:', rf_random_best.score(X_train, y_train))
print('Exactitud luego de búsqueda aleatoria en entrenamiento (Out of Bag):', rf_random_best.oob_score_)
print('Exactitud luego de búsqueda aleatoria en validación:', rf_random_best.score(X_val, y_val))

max_features = [9, 10, 11]
max_depth = [57, 60, 63]
min_samples_leaf = [4]
n_estimators = [1200]

segundo_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_leaf': min_samples_leaf}

print('Los valores a probar en la búsqueda por grilla son:')
pprint(segundo_grid)

from sklearn.model_selection import GridSearchCV

rf = RandomForestClassifier(oob_score = True)
rf_grid = GridSearchCV(estimator = rf,
                        param_grid = segundo_grid,
                        cv = 3,          # Validación cruzada 3-fold
                        verbose=2,
                        n_jobs = -1      # Paralelizar en todos los cores disponibles
                        )
rf_grid.fit(X_train, y_train)

rf_grid_best = rf_grid.best_estimator_

print('Los hiperparámetros del mejor modelo son:')
pprint(rf_grid.best_params_)
print()

print('Exactitud luego de búsqueda en grilla en entrenamiento:', rf_grid_best.score(X_train, y_train))
print('Exactitud luego de búsqueda en grilla en entrenamiento (Out of Bag):', rf_grid_best.oob_score_)
print('Exactitud luego de búsqueda en grilla en validación:', rf_grid_best.score(X_val, y_val))

"""### Curva ROC"""

from sklearn import metrics

y_pred_val = rf_grid_best.predict_proba(X_val)[:,1]
auc_roc = metrics.roc_auc_score(y_val, y_pred_val)
print('AUC =', auc_roc)

metrics.plot_roc_curve(rf_grid_best, X_val, y_val)
plt.show()

"""## Visualización de las características más importantes


"""

feature_names = X_train.columns.values
tree_feature_importances = rf_grid_best.feature_importances_
sorted_idx = tree_feature_importances.argsort()

y_ticks = np.arange(0, len(feature_names))
fig, ax = plt.subplots()
ax.barh(y_ticks, tree_feature_importances[sorted_idx])
ax.set_yticklabels(feature_names[sorted_idx])
ax.set_yticks(y_ticks)
ax.set_title("Random Forest Feature Importances")
fig.tight_layout()
plt.show()

"""# Otros modelos de ensamble

Prueba a entrenar ensambles con por lo menos otras dos [estrategias](https://scikit-learn.org/stable/modules/ensemble.html#). Puedes intentar, por ejemplo, con [AdaBoost](https://scikit-learn.org/stable/modules/ensemble.html#adaboost), [Gradient Boosting](https://scikit-learn.org/stable/modules/ensemble.html#gradient-tree-boosting), [XGBoost](https://xgboost.readthedocs.io/en/latest/python/python_api.html#module-xgboost.sklearn) ([ejemplos](https://github.com/dmlc/xgboost/blob/master/demo/guide-python/sklearn_examples.py)\) o [Apilamiento](https://scikit-learn.org/stable/modules/ensemble.html#stacked-generalization).
"""




