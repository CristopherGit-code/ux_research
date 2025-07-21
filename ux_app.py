import logging
import gradio as gr
from src.modules.UI_manager import UI

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=f'UI_render.{__name__}')

UI_manager = UI()

md_message = UI_manager.get_chat_placeholder()

with gr.Blocks() as ux_app:
    gr.Markdown("""<h1 align="center"> UX Research App </h1>""")
    
    ## Main user state for each session
    chat_init_uuid = gr.State()

    chat_instructions = gr.Textbox(placeholder='Answer in just bullet points...',label='System Instructions', render=False)

    with gr.Tab("Report calls filter"):
        with gr.Row(equal_height=True):
            text_search = gr.Text(label="Search by query:", placeholder="Give me documents in America...")
        
        with gr.Row(equal_height=True):
            unique_study,unique_region,unique_utility,unique_property_type,unique_characteristics = UI_manager.available_filters()
            study = gr.Dropdown(choices=unique_study, interactive=True, label='Study')
            location = gr.Dropdown(choices=unique_region, interactive=True, label='Location')
            utility = gr.Dropdown(choices=unique_utility, interactive=True, label='Utility')
            property_type = gr.Dropdown(choices=unique_property_type, interactive=True, label='Property type')
            characteristics = gr.Dropdown(choices=unique_characteristics, interactive=True, label='Customer characteristics')
            products = gr.Text(label="Products")
            events = gr.Text(label="Topics")
        
        with gr.Row(equal_height=True):
            filter_bttn = gr.Button("Search files")
            message = gr.Text(container=False,interactive=False)
        
        gr.Markdown("""<h2 align="center"> Utilities found </h2>""")
        with gr.Row(equal_height=True):
            file_list = gr.List(show_label=True, show_row_numbers=True, col_count=False)
            
        with gr.Row(equal_height=True):
            new_files = gr.File()
            with gr.Column():
                new_file_bttn = gr.Button("Upload files")
                file_message = gr.Text(container=False,interactive=False)
        
    with gr.Tab("Chat"):
        gr.ChatInterface(
                fn=UI_manager.get_client_analysis, 
                chatbot=gr.Chatbot(height=500, placeholder=md_message ,type='messages',render_markdown=True),
                type="messages",
                additional_inputs=[
                    chat_instructions,
                    chat_init_uuid
                ]
            )                  

    filter_bttn.click(
        UI_manager.get_client_filter,
        inputs=[study,location,utility,property_type,characteristics,products,events,text_search,chat_init_uuid],
        outputs=[file_list, message]
    )

    new_file_bttn.click(
        UI_manager.manage_files,
        inputs=[new_files],
        outputs=[file_message]
    )

    ux_app.load(
        fn = UI_manager.load_user_session,
        inputs=[chat_init_uuid],
        outputs=[chat_init_uuid]
    )

if __name__=='__main__':
    #ux_app.queue(max_size=60).launch(max_threads=6, root_path="/wl-analysis", server_port=6100,show_api=False)
    ux_app.launch(show_api=False)