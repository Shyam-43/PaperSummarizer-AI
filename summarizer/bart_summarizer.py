import logging
from transformers import BartTokenizer, BartForConditionalGeneration
import torch

logger = logging.getLogger(__name__)

class BARTSummarizer:
    """Abstractive summarizer using facebook/bart-large-cnn."""

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Initialized BARTSummarizer")

    def load_model(self):
        logger.info("Loading BART model...")
        self.tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
        self.model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn").to(self.device)
        logger.info("BART model loaded and ready")

    def summarize_text(self, text, max_length=150, min_length=50):
        try:
            inputs = self.tokenizer.batch_encode_plus(
                [text],
                max_length=1024,
                return_tensors="pt",
                truncation=True,
                padding="longest"
            )
            input_ids = inputs["input_ids"].to(self.device)
            attention_mask = inputs["attention_mask"].to(self.device)

            summary_ids = self.model.generate(
                input_ids,
                attention_mask=attention_mask,
                num_beams=4,
                length_penalty=2.0,
                max_length=max_length,
                min_length=min_length,
                early_stopping=True
            )

            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            logger.info(f"Generated summary of {len(summary)} characters")
            return summary

        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return f"Error generating summary: {str(e)}"

    def summarize_batch(self, texts, max_length=150, min_length=50):
        summaries = []
        for i, text in enumerate(texts):
            try:
                summary = self.summarize_text(text, max_length, min_length)
                summaries.append(summary)
            except Exception as e:
                summaries.append(f"Error summarizing text {i + 1}: {str(e)}")
        return summaries

# Global instance
_summarizer = None

def get_summarizer():
    global _summarizer
    if _summarizer is None:
        _summarizer = BARTSummarizer()
        _summarizer.load_model()
    return _summarizer
