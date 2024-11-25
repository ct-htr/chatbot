import streamlit as st
from openai import AzureOpenAI
import requests
import time # built-in Python lib - no need to specify in requirements.txt

# Model of AI used.
aiModel = "gpt-4-turbo"

# Helper function to create the typing effect for responses
def stream_data(streamText):
    for word in streamText.split():
        yield word + " "
        time.sleep(0.03)

# Show title and description.
st.title("💬 ISOM3400 Simple Chatbot")
st.write(
    f"This is a simple chatbot that uses [HKUST's Azure OpenAI API Service](https://itsc.hkust.edu.hk/services/it-infrastructure/azure-openai-api-service). The current version is **{aiModel}**.  \n"
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://hkust.developer.azure-api.net/profile). \n\n"
    "The code is based off of Streamlit's [Chatbot Template](https://share.streamlit.io/template-preview/b8e65aff-d8c7-4b7d-9d4c-eb79249dfc4b).  \n"
    "You can also learn how to build this app step by step by [following Streamlit's tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
apiKey = st.text_input("HKUST Azure OpenAI key", type="password")
if not apiKey:
    st.info("Please add your OpenAI API key to continue. For more information, please visit [the ITSC website](https://itsc.hkust.edu.hk/services/it-infrastructure/azure-openai-api-service). ", icon="🗝️")

else:
    try: 
        balanceApi = "https://hkust.azure-api.net/openai-balance/get"
        headers = {"Cache-Control": "no-cache",
                "api-key": apiKey}

        creditInfo = st.empty() # Placeholder since Streamlit creates the app from top to bottom according to the lines of code.
        
        st.markdown("---")

        #AzureOpenAI code (AzureOpenAI != OpenAI exactly; there are some slight differences. The version provided by UST is AzureOpenAI.
        client = AzureOpenAI(
        api_key = apiKey,
        api_version = '2024-06-01',
        azure_endpoint = 'https://hkust.azure-api.net'
        )

        # Create a session state variable to store the chat messages. This ensures that the
        # messages persist across reruns.
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display the existing chat messages via `st.chat_message`.
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Create a chat input field to allow the user to enter a message. This will display
        # automatically at the bottom of the page.
        if prompt := st.chat_input("What is up?"):

            # Store and display the current prompt.
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API.
            stream = client.chat.completions.create(
                model = aiModel,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
            )

            # Stream the response to the chat using `st.write_stream`, then store it in 
            # session state.
            
            with st.chat_message("assistant"):
                outputStream = stream.model_dump()["choices"][0]["message"]["content"]
                response = st.write_stream(stream_data(outputStream))
            st.session_state.messages.append({"role": "assistant", "content": response})
                
                
        with requests.get(balanceApi, headers=headers) as response: # Update remaining credits after sending a message.
            remainingCredit = response.json()
            if remainingCredit > 0:
                creditInfo.info(f"💳Remaining credit for this month: ${remainingCredit}") # creditInfo is the placeholder space from above.
            else:
                creditInfo.error(f"💳Remaining credit for this month: ${remainingCredit}")
                
    except:
        st.error("⚠️Invalid API key. Please re-enter your key.")
    
