import omni.ext
import omni.ui as ui
import openai
import pandas as pd
from langchain import OpenAI
from langchain.chains import ConversationChain

# Your OpenAI API Key
API_KEY = "your-openai-api-key"  # Replace with your OpenAI API key

# Load the CSV file with inventory data
csv_file = "data/warehouse_inventory.csv"
df = pd.read_csv(csv_file)


class MyAssistantExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[Assistant Extension] Started")

        # Create a simple window with an Assistant button
        self._window = ui.Window("My Assistant Extension", width=300, height=200)

        with self._window.frame:
            with ui.VStack():
                # Assistant button to launch the LangChain chat window
                self.assistant_button = ui.Button("Launch Assistant", clicked_fn=self.launch_assistant)

    def launch_assistant(self):
        """Handler to launch the LangChain chat window when the button is pressed."""
        # Create LangChain conversation chain
        self.chat_chain = ConversationChain(llm=OpenAI(api_key=API_KEY))

        # Create the LangChain Chatbot UI window
        self._chat_window = ui.Window("LangChain Assistant", width=400, height=500)

        with self._chat_window.frame:
            with ui.VStack():
                # Chat history area
                self.chat_history = ui.ScrollingFrame(height=400)
                with self.chat_history:
                    self.chat_output = ui.Label("", word_wrap=True)

                # Input field for user queries
                self.input_field = ui.StringField(placeholder="Ask about warehouse inventory...", height=40)

                # Button to submit the query
                self.send_button = ui.Button("Send", clicked_fn=self.on_send_clicked)

    def on_send_clicked(self):
        """Handler to send user input to LangChain and OpenAI when the user presses Send."""
        # Get user input
        user_input = self.input_field.model.get_value_as_string()

        if user_input:
            # Query the CSV data and form the prompt for OpenAI
            csv_data = self.query_inventory_data(user_input)
            prompt = f"User asks: {user_input}\nRelevant inventory data:\n{csv_data}\n"

            # Get the response from LangChain (via OpenAI)
            response = self.chat_chain.run(input=prompt)

            # Update chat history with user input and assistant's response
            self.update_chat_history(f"You: {user_input}\nAssistant: {response}\n")

    def query_inventory_data(self, query):
        """Search the CSV data for relevant information based on the user query."""
        relevant_rows = []

        # Perform a simple keyword search in the CSV file for relevant inventory data
        for _, row in df.iterrows():
            if query.lower() in row['item_name'].lower() or query.lower() in row['location'].lower():
                relevant_rows.append(f"{row['item_name']} - {row['quantity']} units in {row['location']}")

        # Return the results or a default message if nothing is found
        return "\n".join(relevant_rows) if relevant_rows else "No relevant inventory data found."

    def update_chat_history(self, new_message):
        """Update the chat history with the assistant's response and user input."""
        current_text = self.chat_output.text
        self.chat_output.text = f"{current_text}\n{new_message}"

    def on_shutdown(self):
        """Clean up the windows and resources when the extension shuts down."""
        print("[Assistant Extension] Shutting down")
        if self._window:
            self._window.destroy()
            self._window = None

        if self._chat_window:
            self._chat_window.destroy()
            self._chat_window = None
