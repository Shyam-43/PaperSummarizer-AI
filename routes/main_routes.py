from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
import os
import logging
from werkzeug.utils import secure_filename

from summarizer.text_processor import TextProcessor
from summarizer.pdf_processor import PDFProcessor
from summarizer.url_processor import URLProcessor
from summarizer.bart_summarizer import get_summarizer
from models import Summary
from storage.data_manager import DataManager

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)
data_manager = DataManager()

@main_bp.route('/')
def index():
    """Home page with summarization interface."""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page with feature information."""
    return render_template('about.html')

@main_bp.route('/history')
@login_required
def history():
    """History page showing user's past summaries."""
    user_summaries = data_manager.get_user_summaries(current_user.id)
    return render_template('history.html', summaries=user_summaries)

@main_bp.route('/summarize', methods=['POST'])
@login_required
def summarize():
    """Handle summarization requests for all input types."""
    try:
        input_type = request.form.get('input_type')
        
        if input_type == 'text':
            return handle_text_summarization()
        elif input_type == 'url':
            return handle_url_summarization()
        elif input_type == 'pdf':
            return handle_pdf_summarization()
        elif input_type == 'batch_pdf':
            return handle_batch_pdf_summarization()
        else:
            flash('Invalid input type selected.', 'error')
            return redirect(url_for('main.index'))
            
    except Exception as e:
        logger.error(f"Summarization error: {str(e)}")
        flash(f'An error occurred during summarization: {str(e)}', 'error')
        return redirect(url_for('main.index'))

def handle_text_summarization():
    """Handle text input summarization."""
    text_input = request.form.get('text_content', '').strip()
    
    if not text_input:
        flash('Please enter some text to summarize.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Process text
        processed_text = TextProcessor.process_text(text_input)
        
        # Generate summary
        summarizer = get_summarizer()
        summary = summarizer.summarize_text(processed_text)
        
        # Save to history
        summary_obj = Summary(
            user_id=current_user.id,
            input_type='text',
            content=processed_text[:500] + '...' if len(processed_text) > 500 else processed_text,
            summary=summary
        )
        summary_obj.save(data_manager)
        
        flash('Text summarized successfully!', 'success')
        return render_template('index.html', 
                             summary=summary, 
                             input_type='text',
                             original_content=processed_text[:200] + '...' if len(processed_text) > 200 else processed_text)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('main.index'))

def handle_url_summarization():
    """Handle URL content summarization."""
    url_input = request.form.get('url_content', '').strip()
    
    if not url_input:
        flash('Please enter a URL to summarize.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Extract content from URL
        content = URLProcessor.extract_content_from_url(url_input)
        
        # Generate summary
        summarizer = get_summarizer()
        summary = summarizer.summarize_text(content)
        
        # Save to history
        summary_obj = Summary(
            user_id=current_user.id,
            input_type='url',
            content=f"URL: {url_input}\n\n{content[:500] + '...' if len(content) > 500 else content}",
            summary=summary
        )
        summary_obj.save(data_manager)
        
        flash('URL content summarized successfully!', 'success')
        return render_template('index.html', 
                             summary=summary, 
                             input_type='url',
                             original_url=url_input,
                             original_content=content[:200] + '...' if len(content) > 200 else content)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('main.index'))

def handle_pdf_summarization():
    """Handle single PDF file summarization."""
    if 'pdf_file' not in request.files:
        flash('Please select a PDF file to upload.', 'error')
        return redirect(url_for('main.index'))
    
    file = request.files['pdf_file']
    
    if not file or file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('main.index'))
    
    if not PDFProcessor.validate_pdf_file(file):
        flash('Please upload a valid PDF file (max 10MB).', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = PDFProcessor.save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
        
        # Extract text from PDF
        content = PDFProcessor.extract_text_from_pdf(file_path)
        
        # Generate summary
        summarizer = get_summarizer()
        summary = summarizer.summarize_text(content)
        
        # Save to history
        summary_obj = Summary(
            user_id=current_user.id,
            input_type='pdf',
            content=content[:500] + '...' if len(content) > 500 else content,
            summary=summary,
            original_filename=filename
        )
        summary_obj.save(data_manager)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        flash('PDF summarized successfully!', 'success')
        return render_template('index.html', 
                             summary=summary, 
                             input_type='pdf',
                             original_filename=filename,
                             original_content=content[:200] + '...' if len(content) > 200 else content)
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('main.index'))

def handle_batch_pdf_summarization():
    """Handle batch PDF file summarization."""
    if 'batch_pdf_files' not in request.files:
        flash('Please select PDF files to upload.', 'error')
        return redirect(url_for('main.index'))
    
    files = request.files.getlist('batch_pdf_files')
    
    if not files or all(f.filename == '' for f in files):
        flash('No files selected.', 'error')
        return redirect(url_for('main.index'))
    
    # Validate files
    valid_files = []
    for file in files:
        if file and file.filename != '' and PDFProcessor.validate_pdf_file(file):
            valid_files.append(file)
    
    if not valid_files:
        flash('No valid PDF files found. Please upload valid PDF files (max 10MB each).', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Save uploaded files
        file_paths = []
        filenames = []
        for file in valid_files:
            filename = secure_filename(file.filename)
            file_path = PDFProcessor.save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
            file_paths.append(file_path)
            filenames.append(filename)
        
        # Process batch PDFs
        results = PDFProcessor.process_batch_pdfs(file_paths)
        
        # Extract successful results
        successful_texts = []
        successful_names = []
        failed_files = []
        
        for i, (filename, content, success, error) in enumerate(results):
            if success:
                successful_texts.append(content)
                successful_names.append(filename)
            else:
                failed_files.append((filename, error))
        
        if not successful_texts:
            flash('No PDF files could be processed successfully.', 'error')
            return redirect(url_for('main.index'))
        
        # Generate summaries
        summarizer = get_summarizer()
        summaries = summarizer.summarize_batch(successful_texts)
        
        # Save to history
        batch_summary = "\n\n".join([
            f"**{name}:**\n{summary}" 
            for name, summary in zip(successful_names, summaries)
        ])
        
        summary_obj = Summary(
            user_id=current_user.id,
            input_type='batch_pdf',
            content=f"Batch processing of {len(successful_names)} files: {', '.join(successful_names)}",
            summary=batch_summary,
            original_filename=f"{len(successful_names)} files"
        )
        summary_obj.save(data_manager)
        
        # Clean up uploaded files
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except:
                pass
        
        success_msg = f'Successfully summarized {len(successful_names)} PDF files!'
        if failed_files:
            success_msg += f' {len(failed_files)} files failed to process.'
        
        flash(success_msg, 'success')
        return render_template('index.html', 
                             batch_summaries=list(zip(successful_names, summaries)),
                             input_type='batch_pdf',
                             failed_files=failed_files)
        
    except Exception as e:
        logger.error(f"Batch PDF processing error: {str(e)}")
        flash(f'Error processing PDF files: {str(e)}', 'error')
        return redirect(url_for('main.index'))
