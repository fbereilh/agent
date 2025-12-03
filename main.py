"""Main FastHTML application for restaurant recommendations."""

from fasthtml.common import *
from agent import RestaurantAgent
from mistletoe import markdown
from lisette.core import Message

# Custom colors
custom_colors = Style("""
:root {
  --color-primary: oklch(62% 0.145 156.96);
  --color-secondary: oklch(35% 0.02 270);
  --color-accent: oklch(75% 0.22 45);
}
""")

# DaisyUI headers
daisy_hdrs = (
    Link(href='https://cdn.jsdelivr.net/npm/daisyui@5', rel='stylesheet', type='text/css'),
    Script(src='https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4'),
    Script(src='https://unpkg.com/htmx-ext-sse@2.2.1/sse.js'),
    custom_colors
)

# Initialize FastHTML app
app = FastHTML(hdrs=daisy_hdrs)
rt = app.route

# Initialize agent (singleton)
agent = RestaurantAgent(db_path="chromadb")


def should_show_message(msg):
    """Determine if a message should be displayed to the user."""
    # Show user messages (dicts with role='user')
    if isinstance(msg, dict) and msg.get('role') == 'user':
        return True
    
    
    # Show assistant Message objects that have content (no tool calls)
    if isinstance(msg, Message) and msg.content and not msg.tool_calls:
        return True
    
    return False


def chat_bubble(msg):
    """Render a chat message bubble."""
    # Handle both dict and Message object
    if isinstance(msg, Message):
        role = msg.role
        content = msg.content
    else:
        role = msg.get('role', 'assistant')
        content = msg.get('content', '')
    
    is_user = role == 'user'
    placement = 'chat-end' if is_user else 'chat-start'
    color = 'chat-bubble-primary' if is_user else 'chat-bubble-secondary'
    
    # Convert markdown to HTML for display
    content_html = markdown(content)
    
    return Div(cls=f'chat {placement}')(
        Div(cls='chat-header')(role),
        Div(NotStr(content_html), cls=f'chat-bubble {color}')
    )


def chat_messages(history):
    """Render all chat messages."""
    return Div(
        id='chat-messages',
        cls='flex-1 overflow-y-auto p-4 space-y-4'
    )(*[chat_bubble(msg) for msg in history if should_show_message(msg)])


def chat_input():
    """Render chat input form."""
    return Form(
        hx_post='/send',
        hx_swap='none',
        cls='flex gap-2 p-4 border-t'
    )(
        Input(
            type='text',
            name='message',
            id='message-input',
            placeholder='¿Qué tipo de comida buscas?',
            cls='input input-bordered flex-1',
            required=True,
            autofocus=True
        ),
        Button('Enviar', type='submit', cls='btn btn-primary')
    )


@rt('/')
def get():
    """Main page."""
    return Div(cls='flex items-center justify-center min-h-screen bg-base-100 p-4')(
        Div(cls='flex flex-col w-full max-w-4xl mx-auto h-[80vh] shadow-xl rounded-lg overflow-hidden')(
            # Header
            Div(cls='navbar bg-base-200')(
                Div(cls='flex-1')(
                    H1('🍽️ Asistente de Restaurantes', cls='text-xl font-bold')
                )
            ),
            
            # Chat area
            chat_messages(agent.history),
            
            # Input
            Div(id='chat-form-container')(
                chat_input()
            ),
            
            # Scripts
            Script("""
                let eventSource = null;
                
                // Auto-scroll
                htmx.on('#chat-messages', 'htmx:afterSwap', function(evt) {
                    const el = evt.detail.target;
                    el.scrollTop = el.scrollHeight;
                });
                
                // Handle form submission
                htmx.on('htmx:afterRequest', function(evt) {
                    if (evt.detail.pathInfo.requestPath === '/send') {
                        const streamId = evt.detail.xhr.getResponseHeader('X-Stream-Id');
                        if (streamId) {
                            // Clear input immediately
                            document.getElementById('message-input').value = '';
                            
                            // Close existing connection
                            if (eventSource) eventSource.close();
                            
                            // Connect to SSE stream
                            eventSource = new EventSource('/stream/' + streamId);
                            
                            eventSource.onmessage = function(e) {
                                const data = JSON.parse(e.data);
                                const messagesDiv = document.getElementById('chat-messages');
                                
                                if (data.type === 'content') {
                                    // Update streaming message
                                    let streamDiv = document.getElementById('streaming-message');
                                    if (!streamDiv) {
                                        streamDiv = document.createElement('div');
                                        streamDiv.id = 'streaming-message';
                                        streamDiv.className = 'chat chat-start';
                                        streamDiv.innerHTML = '<div class="chat-header">assistant</div><div class="chat-bubble chat-bubble-secondary"></div>';
                                        messagesDiv.appendChild(streamDiv);
                                    }
                                    streamDiv.querySelector('.chat-bubble').textContent = data.content;
                                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                                } else if (data.type === 'done') {
                                    // Close connection and reload messages
                                    eventSource.close();
                                    htmx.ajax('GET', '/messages', {target: '#chat-messages', swap: 'innerHTML'});
                                }
                            };
                        }
                    }
                });
            """)
        )
    )


import uuid
from threading import Thread
from queue import Queue

# Store active streams
streams = {}

@rt('/send')
def post(message: str):
    """Handle user message - initiate streaming."""
    # Generate stream ID
    stream_id = str(uuid.uuid4())
    
    # Create queue for this stream
    q = Queue()
    streams[stream_id] = q
    
    # Start background thread to process message
    def process():
        from litellm import ModelResponseStream
        
        # Add user message to display
        agent.chat.hist.append({'role': 'user', 'content': message})
        
        # Stream response
        res_gen = agent.chat('', stream=True)  # Empty since message already added
        content = ""
        
        try:
            for chunk in res_gen:
                if isinstance(chunk, ModelResponseStream):
                    delta = chunk.choices[0].delta.content
                    if delta:
                        content += delta
                        q.put({'type': 'content', 'content': content})
            
            # Signal completion
            q.put({'type': 'done'})
        finally:
            q.put(None)  # Signal end of stream
    
    Thread(target=process, daemon=True).start()
    
    # Return response with stream ID in header
    from starlette.responses import Response
    return Response('', headers={'X-Stream-Id': stream_id})


@rt('/stream/{stream_id}')
def get_stream(stream_id: str):
    """SSE endpoint for streaming responses."""
    import json
    
    def generate():
        q = streams.get(stream_id)
        if not q:
            return
        
        try:
            while True:
                msg = q.get()
                if msg is None:
                    break
                yield f"data: {json.dumps(msg)}\n\n"
        finally:
            # Cleanup
            streams.pop(stream_id, None)
    
    from starlette.responses import StreamingResponse
    return StreamingResponse(generate(), media_type='text/event-stream')


@rt('/messages')
def get_messages():
    """Get current chat messages."""
    return chat_messages(agent.history)


if __name__ == '__main__':
    serve()
