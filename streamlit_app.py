# streamlit_app.py

import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from psycopg2 import Error
import numpy as np


connection = psycopg2.connect(user="vyzgmpqsxeucnv",
                            password="480540f32aa53c6f6850fee0add13f0ae8211a9aa7c98ed18fab701a829869df",
                            host="ec2-54-157-79-121.compute-1.amazonaws.com",
                            port="5432",
                            database="d1evcvc2sccml6")
#Creamos el cursor para las operaciones de la base de datos
cursor = connection.cursor()
#Creamos una variable con el codigo sql que queremos que se ejecute
select_query = '''SELECT *
FROM PUBLIC.accommodations a
JOIN PUBLIC.cities c ON c.city_id = a.id_city
ORDER BY a.id;'''
#Executamos el comando
cursor.execute(select_query)
connection.commit()
#con la funcion fetchall() podemos ver lo que retornaria la base de datos
#df_accommodations = cursor.fetchall()
#print(df_accommodations)
#Esto crea un data frame con la información que pediste de la base de datos
df = pd.read_sql_query(select_query,connection)
# st.write("Result: ", cursor.fetchall())


#'''Este es el codigo que se utiliza para la primer visualización, Top 5 Numero de visitas por ciudad ''', con estas comillas se puede imprimir 
#en pantalla de streamlit lo que quieras

#Agrupamos por el nombre de las ciudades y sumamos las visitas que han tenido por toda la ciudad
df_groupby_ciudad_visitas = df.groupby(by='name')['number_of_visits'].agg([sum, min, max])

#Reseteamos los index para que 'name' se ponga como columna y no se quede en indice
df_groupby_ciudad_visitas = df_groupby_ciudad_visitas.reset_index()

#Ordenamos el df por el 'sum' para que esten ordenados del que tiene mas visitas al que tiene menos
df_groupby_ciudad_visitas = df_groupby_ciudad_visitas.sort_values('sum', ascending=False)

#Codigo para imprimir el grafico creado con matplotlib
st.subheader('TOP 5 (visitas por ciudad)')
x = df_groupby_ciudad_visitas['name'][:5]
y = df_groupby_ciudad_visitas['sum'][:5]
fig_top5 = plt.figure(figsize = (10, 5))
plt.bar(x, y, color='red')
plt.xlabel('Ciudad')
plt.ylabel('Visitas')
# plt.title('TOP 5 visitas por ciudad')
st.pyplot(fig_top5)

#Codigo para segunda visualización, Top 10 Numero de visitas por ciudad
st.subheader('TOP 10 (visitas por ciudad)')
x = df_groupby_ciudad_visitas['name'][:10]
y = df_groupby_ciudad_visitas['sum'][:10]
fig_top10 = plt.figure(figsize = (10, 5))
plt.barh(x, y, color='blue')
plt.xlabel('Ciudad')
plt.ylabel('Visitas')
st.pyplot(fig_top10)

#Creamos la visualización del tiempo promedio de estacia por ciudad
#Creamos el dataframe
df_average_night_per_city = df.groupby(by='name')['average_nights'].agg(['mean', 'median'])
df_average_night_per_city = df_average_night_per_city.reset_index()
st.dataframe(df_average_night_per_city)




# == Min and max prices by city

select_query = '''select min(a.price), max(a.price), c."name"
   	from public.accommodations a
   	join public.cities c on c.city_id = a.id_city 
   	group by c."name"
   	order by c."name"'''

cursor.execute(select_query)
connection.commit()

df = pd.read_sql_query(select_query,connection)

t = np.arange(0.01, 10.0, 0.01)
df_cities = df['name']
df_min = df['min']
df_max = df['max']

st.subheader('Min and max prices by city')

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('cities')
ax1.set_ylabel('min prices', color=color)
ax1.plot(df_cities, df_min, color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('max prices', color=color)  # we already handled the x-label with ax1
ax2.plot(df_cities, df_max, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
st.pyplot(fig)

min_max_prices_city = plt.figure(figsize = (10, 5))

plt.fill_between(df_cities, df_min, color="skyblue", alpha=0.5, label='Min price')
plt.fill_between(df_cities, df_max, color="lightpink", alpha=0.5, label='Max price')

plt.legend()
st.pyplot(min_max_prices_city)

# =

# == Guest capacity by city

select_query = '''select PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY a.person_capacity), c."name"
   from public.accommodations a
   join public.cities c on c.city_id = a.id_city 
   group by c."name"
   order by c."name";'''

cursor.execute(select_query)
connection.commit()

df = pd.read_sql_query(select_query,connection)

df_cities = df['name']
df_capacity = df['percentile_cont']

st.subheader('Guest capacity by city')

guest_capacity_city, ax1 = plt.subplots()
ax1.pie(df_capacity, labels=df_cities, autopct='%.1f')

st.pyplot(guest_capacity_city)

# =



# st.subheader('The new chart')
# # Pie chart, where the slices will be ordered and plotted counter-clockwise:
# labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
# sizes = [15, 30, 45, 10]
# explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')


# fig1, ax1 = plt.subplots()
# ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        # shadow=True, startangle=90)
# ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

# st.pyplot(fig1)

if (connection):
  cursor.close()
  connection.close()
  print("PostgreSQL connection is closed")
