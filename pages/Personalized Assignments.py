import streamlit as st
from pydantic import BaseModel
import json
from connect_with_them.tools import CONNECT
#from connect_with_them.Prompts import Prompt_query

# Title for Streamlit app
st.title("Executor Tool")

# Form for user input
with st.form("executor_form"):
    grade = st.text_input("Enter Grade")
    subject = st.text_input("Enter Subject")
    description = st.text_area("Enter Description")

    # Form submit button
    submitted = st.form_submit_button("Execute")

if submitted:
    if not (grade and subject):
        st.error("Grade and subject are required.")
    else:
        try:
            # Prepare the user input for the prompt
            gen = CONNECT(grade,subject,description)

            # Call the Agent_executor with the input
            result = gen.run()
            st.json(result)
            for keys in result:
                try:
                    text = ""
                    text = text + f"**{keys['project title']}**:\n\n"
                    text = text + f"**Project**: {keys['recommendation']}:\n\n"
                    text = text + f"**Reasoning**: {keys['rationale']}:\n\n"
                    with st.expander("Project"):
                        st.write(text)
                except:
                    with st.expander("More Info"):
                        st.write(result[keys])
            st.json(result)
            st.success("Execution completed successfully!")
            #st.json(output)

        except Exception as e:
            error_message = f"Error in executor: {e}"
            st.error(error_message)
