import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import os
import soundfile as sf
import requests

def download_file(url):
    # Estrai l'ID del file dal link di Google Drive
    file_id = url.split('/')[-2]

    # Crea il link di download diretto
    download_url = f'https://docs.google.com/uc?export=download&id={file_id}'

    # Scarica il file
    response = requests.get(download_url, allow_redirects=True)
    local_filename = url.split('/')[-1] + '.wav'
    open(local_filename, 'wb').write(response.content)

    return local_filename

def main():
    # Gradio Interface
    with gr.Blocks() as app:
        gr.Markdown(
            """
            # <div align="center"> Ilaria Audio Analyzer 💖 </div>
            Audio Analyzer Software by Ilaria, Help me on [Ko-Fi!](https://ko-fi.com/ilariaowo)\n
            Special thanks to Alex Murkoff for helping me coding it!
    
            Need help with AI? Join [Join AI Hub!](https://discord.gg/aihub)
            """
        )
    
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(type='filepath')
                create_spec_butt = gr.Button(value='Create Spectrogram And Get Info', variant='primary')

            with gr.Column():
                output_markdown = gr.Markdown(value="", visible=True)
                image_output = gr.Image(type='filepath', interactive=False)
            
                with gr.Accordion('Audio Downloader', open=False):
                    url_input = gr.Textbox(value='', label='Google Drive Audio URL')
                    download_butt = gr.Button(value='Download audio', variant='primary')
                
                download_butt.click(fn=download_file, inputs=[url_input], outputs=[audio_input])
                create_spec_butt.click(fn=create_spectrogram_and_get_info, inputs=[audio_input], outputs=[output_markdown, image_output])
            
        download_butt.click(fn=download_file, inputs=[url_input], outputs=[audio_input])
        create_spec_butt.click(fn=create_spectrogram_and_get_info, inputs=[audio_input], outputs=[output_markdown, image_output])
        
        app.queue(max_size=1022).launch(share=True)

def create_spectrogram_and_get_info(audio_file):
    # Clear figure in case it has data in it
    plt.clf()
    
    # Read the audio data from the file
    audio_data, sample_rate = sf.read(audio_file)

    # Convert to mono if it's not mono
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)

    # Create the spectrogram
    plt.specgram(audio_data, Fs=sample_rate / 1, NFFT=4096, sides='onesided',
                 cmap="Reds_r", scale_by_freq=True, scale='dB', mode='magnitude', window=np.hanning(4096))

    # Save the spectrogram to a PNG file
    plt.savefig('spectrogram.png')

    # Get the audio file info
    audio_info = sf.info(audio_file)
    
    bit_depth = {'PCM_16': 16, 'FLOAT': 32}.get(audio_info.subtype, 0)
    
    # Convert duration to minutes, seconds, and milliseconds
    minutes, seconds = divmod(audio_info.duration, 60)
    seconds, milliseconds = divmod(seconds, 1)
    milliseconds *= 1000  # convert from seconds to milliseconds
    
    # Convert bitrate to mb/s
    bitrate = audio_info.samplerate * audio_info.channels * bit_depth / 8 / 1024 / 1024
    
    # Calculate speed in kbps
    speed_in_kbps = audio_info.samplerate * bit_depth / 1000
    
    # Create a table with the audio file info
    filename_without_extension, _ = os.path.splitext(os.path.basename(audio_file))
    info_table = f"""
    
    | Information | Value |
    | :---: | :---: |
    | File Name | {filename_without_extension} |
    | Duration | {int(minutes)} minutes - {int(seconds)} seconds - {int(milliseconds)} milliseconds |
    | Bitrate | {speed_in_kbps} kbp/s |
    | Audio Channels | {audio_info.channels} |
    | Samples per second | {audio_info.samplerate} Hz |
    | Bit per second | {audio_info.samplerate * audio_info.channels * bit_depth} bit/s |
    
    """
    
    # Return the PNG file of the spectrogram and the info table
    return info_table, 'spectrogram.png'

# Create the Gradio interface
main()
