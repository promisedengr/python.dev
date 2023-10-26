import base64
from io import BytesIO

def fig_to_html(fig):
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    html = '<img class="img-fluid" src=\'data:image/png;base64,{}\'>'.format(encoded)
    return html