import streamlit as st

st.set_page_config(
    page_title="multipage App",
    page_icon=""
)

st.subheader("Introduction")
st.markdown("The main objectives of this project is to:-  \n"
        "(i) predict future Covid cases/deaths in a 30-60day timeframe using a logistic regression model;  \n"
        "(ii) perform a high level analysis of the relationship between social distancing worldwide and in Hong Kong.")

st.subheader("Datasets used")
st.markdown("Throughout this project, I mainly used datasets from 2 sources. The first, being the John Hopkins University time-series Covid dataset, shows Covid cases and deaths by countries and regions over time. This dataset is prepared by John Hopkins University, a reputable medical school in the US. Please also note that John Hopkins has ceased to update their dataset as of 10 March 2023, as such, all the data show in Tab 1 (“1.Covid_Projection”) are only updated to that date. \n"
            "The second data set, being the Facebook mobility dataset, is prepared by Facebook through the collection of anonymised location data from its users. The dataset is made available to the public to assist public health researchers to better understand the effectiveness of social distancing on controlling the Covid outbreak. The Facebook mobility dataset includes an index developed by Facebook to track the average movement trends of its users in a country/region over time. A higher mobility index means that the Facebook users in that particular region are locationally more active (i.e., travelling more) and practices less social distancing measures (and vice versa).")

st.subheader("Findings/observations")
st.markdown("1.Covid Projection (first tab)  \n"
            "As mentioned above, I used a logistic regression model to predict the future Covid cases/deaths in a 30-60 day timeframe. I did this by, first of all, “smoothing” the cumulative data using the LOWESS (locally weighted scatterplot smoothing) method. Then, used the least_squares method form the “script.optimize” library to train the model over a preset timeframe. The model training period has been set to 30days as default (i.e., logistic regression is applied to a 30 day dataset for training). The model training period can be adjusted on the sidebar. You may wish to read “Models.py” file for the detailed steps taken to train the data.  \n  \n"
            "To better visualise the logistic regression model, I have also includes display options to visualise the length of the training period and the tail end of the regression model in the sidebar. Furthermore, users can also chose apply the model on either Covid cases or Covid deaths.  \n  \n"
            "The first graph, shows cumulative Covid cases/deaths. The second graph, shows daily Covid cases/deaths, which is derived by taking the day-to-day difference between the first graph (i.e., the smoothed cumulative Covid data) and re-graphing the same data.  \n  \n"
            "Overall, from a high level perspective, I would say that using logistic regression to model Covid cases/deaths seems to be generally accurate. It is noted that if the model training period is shorter (i.e., say shorter than 10 days), the model tends to significantly deviate from the actual Covid data.  \n  \n"
            "2. Covid Social distancing (second tab)  \n  \n"
            "In the second tab, I have plotted 2 graphs using Plotly for a high level analysis on the effectiveness of social distancing on controlling Covid. The first graph is an animated graph displaying the relationship between a country’s mobility index and the number of Covid cases over time. The goal of this animation is to identify any cultural factors, say between Eastern and Western countries, on the populations’s adherence to social distancing measures and its effect of Covid cases. Obviously, this is an overly ambitious goal that is hard to quantify and test. Nevertheless, the graph could serve as a reference for future investigations into the subject.  \n  \n"
            "The second graph shows the mobility index in Hong Kong over time. I have also aded an additional option on the sidebar to display the daily Covid cases. Based on the second graph, there seems to be a relationship between the mobility index, an indicator of social distancing, and Covid cases in Hong Kong. The graph seems to imply that a higher mobility index (i.e., less social distancing) could lead to higher number of Covid cases in Hong Kong. Please note, however, that there is a lack of understanding in the causal relationship between these two factors, especially when there are other factors to effect social distancing (i.e., government policies).")

st.sidebar.success("Select a page above")


### Make Dashboard

