import streamlit as st
import numpy as np
import pandas as pd

def example1() :
    st.write("Example 1")
    df = pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
    })
    df

def example2() :
    st.write("Example 2")
    st.write("Here's our first attempt at using data to create a table:")
    st.write(pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
    }))

def example3() :
    st.write("Example 3")
    dataframe = np.random.randn(10, 20)
    st.dataframe(dataframe)

def example4() :
    st.write("Example 4")
    dataframe = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))

    st.dataframe(dataframe.style.highlight_max(axis=0))

def example5() :
    st.write("Example 5")
    dataframe = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))
    st.table(dataframe)

def example6() :
    st.write("Example 6")
    chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c'])

    st.line_chart(chart_data)

def example7() :
    st.write("Example 7")
    map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

    st.map(map_data)

def example8() :
    st.write("Widget 1")
    x = st.slider('x')  # 👈 this is a widget
    st.write(x, 'squared is', x * x)

def example9() :
    st.write("Widget 2")
    st.text_input("Your name", key="name")

    # You can access the value at any point with:
    st.session_state.name

def example10() :
    st.write("Example 10")
    if st.checkbox('Show dataframe'):
        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['a', 'b', 'c']
        )

        chart_data

def example11() :
    st.write("Example 11")
    df = pd.DataFrame({
        'first column': [1, 2, 3, 4],
        'second column': [10, 20, 30, 40]
    })

    option = st.selectbox(
        'Which number do you like best?',
         df['first column']
    )

    'You selected: ', option

def example12() :
    st.write("Example 12")
    # Add a selectbox to the sidebar:
    add_selectbox = st.sidebar.selectbox(
        'How would you like to be contacted?',
        ('Email', 'Home phone', 'Mobile phone')
    )

    # Add a slider to the sidebar:
    add_slider = st.sidebar.slider(
        'Select a range of values',
        0.0, 100.0, (25.0, 75.0)
    )


def main() :
    example1()
    example2()
    example3()
    example4()
    example5()
    example6()
    example7()
    example8()
    example9()
    example10()
    example11()
    example12()

if __name__ == "__main__" :
    main()



