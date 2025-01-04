from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import plotly
import plotly.graph_objs as go
import json
import base64
import re
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'static/images')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-profile', methods=['GET', 'POST'])
def upload_profile():
    if request.method == 'GET':
        return render_template('upload_profile.html')
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return jsonify({'success': True, 'filename': filename})

@app.route('/save-crop', methods=['POST'])
def save_crop():
    try:
        data = request.json
        image_data = data['imageData']
        
        # Extract the base64 data after the comma
        image_data = re.sub('^data:image/.+;base64,', '', image_data)
        
        # Decode base64 string to bytes
        image_bytes = base64.b64decode(image_data)
        
        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'profile_{timestamp}.jpg'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Add debug logging
        print(f"Saving image to: {filepath}")
        
        # Save the image
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
            
        return jsonify({
            'success': True,
            'filename': filename
        })
        
    except Exception as e:
        print(f"Error in save_crop: {str(e)}")  # Add debug logging
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def create_pie_chart():
    # Sample data for the pie chart
    labels = ['Python', 'JavaScript/TypeScript', 'HTML', 'CSS', 'SQL']
    values = [40, 25, 15, 15, 5]
    
    # Create the pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker=dict(colors=['#3B82F6', '#F7DF1E', '#E34F26', '#1572B6', '#336791']),
        hovertemplate="<b>%{label}</b><br>" +
                      "%{percent}<br>" +
                      "<extra></extra>"
    )])
    
    # Update the layout for dark theme
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        margin=dict(t=0, b=0, l=0, r=0),
        showlegend=True,
        legend=dict(
            font=dict(color='#ffffff'),
            bgcolor='rgba(0,0,0,0)'
        )
    )
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/')
def index():
    # Get the pie chart JSON
    pie_chart = create_pie_chart()
    return render_template('index.html', pie_chart=pie_chart)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    # Example project data
    projects = [
        {
            'title': 'Project 1',
            'description': 'A web application built with Flask and TailwindCSS',
            'tech_stack': ['Python', 'Flask', 'TailwindCSS']
        },
        {
            'title': 'Project 2',
            'description': 'Mobile app development using React Native',
            'tech_stack': ['JavaScript', 'React Native', 'Redux']
        },
        {
            'title': 'Project 3',
            'description': 'Machine Learning project for image classification',
            'tech_stack': ['Python', 'TensorFlow', 'OpenCV']
        }
    ]
    return render_template('projects.html', projects=projects)

@app.route('/blog')
def blog():
    # Example blog posts
    posts = [
        {
            'title': 'Getting Started with Flask',
            'date': 'March 15, 2024',
            'preview': 'Learn how to build web applications with Flask, a lightweight Python web framework...',
            'read_time': '5 min read',
            'tags': ['Python', 'Web Development', 'Flask']
        },
        {
            'title': 'Mastering TailwindCSS',
            'date': 'March 10, 2024',
            'preview': 'Discover the power of utility-first CSS and how to build modern interfaces...',
            'read_time': '4 min read',
            'tags': ['CSS', 'TailwindCSS', 'Frontend']
        },
        {
            'title': 'Data Visualization with Plotly',
            'date': 'March 5, 2024',
            'preview': 'Create interactive and beautiful data visualizations using Plotly...',
            'read_time': '6 min read',
            'tags': ['Python', 'Data Science', 'Plotly']
        }
    ]
    return render_template('blog.html', posts=posts)

if __name__ == '__main__':
    # For local development only
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 