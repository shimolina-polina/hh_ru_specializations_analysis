import pandas as pd
import streamlit as st
import plotly.express as px
import re



def main():
    # Загрузка данных с вакансиями
    df = pd.read_csv('data/vacancies.csv')

    # Применение фильтров
    filtered_df = df

    # Фильтр по специальности
    main_filter = st.sidebar.radio('Выберите специальность', ['1C консультант', 'Бухгалтер'])

    if main_filter == '1C консультант':
        filtered_df = filtered_df[filtered_df['analysis_field'] == '1C консультант']
    elif main_filter == 'Бухгалтер':
        filtered_df = filtered_df[filtered_df['analysis_field'] == 'Бухгалтер']
    row_count = len(filtered_df)


    # Фильтры по опыту и зарплате
    experience_options = df['experience'].unique()
    salary_from_min = int(df['salary from'].min())
    salary_from_max = int(df['salary from'].max())
    salary_to_min = int(df['salary to'].min())
    salary_to_max = int(df['salary to'].max())

    # Фильтр по опыту с множественным выбором
    experience_filter = st.sidebar.multiselect('Выберите опыт', experience_options)
    if experience_filter:
        filtered_df = filtered_df[filtered_df['experience'].isin(experience_filter)]

    # Слайдеры для зарплаты
    salary_from_filter = st.sidebar.slider('Минимальная зарплата (от)', salary_from_min, salary_from_max, step=1000, value=salary_from_min)
    salary_to_filter = st.sidebar.slider('Максимальная зарплата (до)', salary_to_min, salary_to_max, step=1000, value=salary_to_max)
    filtered_df = filtered_df[
        ((filtered_df['salary from'] >= salary_from_filter) & 
        (filtered_df['salary to'] <= salary_to_filter)) |
        ((filtered_df['salary from'] >= salary_from_filter) &
        (filtered_df['salary to'].isnull()) &
        (filtered_df['salary from'] <= salary_to_filter)) | 
        ((filtered_df['salary from'].isnull()) &  
        (filtered_df['salary to'] <= salary_to_filter) &
        (filtered_df['salary to'] >= salary_from_filter)) |
        ((filtered_df['salary from'].isnull()) & 
        (filtered_df['salary to'].isnull()))
    ]

    filtered_df = filtered_df.rename(columns={'name': 'Название', 'experience': 'Опыт работы', 'alternate_url': 'Ссылка', 'salary from': 'Зарплата от', 'salary to': 'Зарплата до', 'key_skills': 'Ключевые навыки'})



    unique_skills = []
    for values in filtered_df['Ключевые навыки']:

        values = str(values).strip('[]').split(', ')

        for skill in values:
            if skill not in unique_skills and skill != "'nan'" and skill != "''" and skill != "":
                unique_skills.append(skill)

    unique_skills = [re.sub("'","", skill) for skill in unique_skills]
    unique_skills = [x for x in unique_skills if str(x) != "nan"]            

    selected_skills = st.sidebar.multiselect('Выберите навыки', unique_skills)
    filtered_df['Ключевые навыки'] = filtered_df['Ключевые навыки'].astype(object)
    filtered_df = filtered_df[filtered_df['Ключевые навыки'].apply(lambda x: any(skill in str(x) for skill in selected_skills) if selected_skills else True)]

    # Таблички с количеством вакансий
    st.success(f"Количество вакансий: {row_count}")

    # График количество вакансий в зависимости от зарплаты для разных стажей

    df = filtered_df.groupby(['Опыт работы', 'Зарплата от']).count()['id'].reset_index()

    fig_salary_from_experience = px.bar(df, x='Зарплата от', y='id', color='Опыт работы', 
                barmode='group', title='Распределение нижних границ зарплат')

    fig_salary_from_experience.update_layout(xaxis_title='Зарплата от, тыс. руб.',
                    yaxis_title='Количество вакансий')

    st.plotly_chart(fig_salary_from_experience)

    df = filtered_df.groupby(['Опыт работы', 'Зарплата до']).count()['id'].reset_index()

    fig_salary_to_experience = px.bar(df, x='Зарплата до', y='id', color='Опыт работы', 
                barmode='group', title='Распределение верхних границ зарплат')

    fig_salary_to_experience.update_layout(xaxis_title='Зарплата до, тыс. руб.',
                    yaxis_title='Количество вакансий')
    st.plotly_chart(fig_salary_to_experience)

    # График количество вакансий в зависимости от опыта
    fig_experience_counts = px.bar(filtered_df.groupby('Опыт работы')['id'].count().reset_index(), x='Опыт работы', y='id', title='Распределение вакансий по опыту работы')
    st.plotly_chart(fig_experience_counts)

    skills_counts = {}

    for skill in unique_skills:
        skill = re.escape(skill)
        skills_counts[skill] = filtered_df['Ключевые навыки'].str.count(skill).sum()
        
    sorted_skills_counts = dict(sorted(skills_counts.items(), key=lambda x: x[1], reverse=True))

    top_10_df = pd.DataFrame(list(sorted_skills_counts.items())[:10])
    top_10_df.columns = ['Навык', 'Количество']

    fig = px.bar(top_10_df, x='Навык', y='Количество', title='Топ-10 навыков')
    st.plotly_chart(fig, use_container_width=True)

    # Таблица вакансий
    st.write(filtered_df[['Название', 'Опыт работы', 'Ссылка', 'Зарплата от', 'Зарплата до', 'Ключевые навыки']])


if __name__ == "__main__":
    main()
