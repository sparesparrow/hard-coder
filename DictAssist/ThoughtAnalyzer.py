
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta
import openai
from collections import defaultdict

class ThoughtAnalyzer:
    def __init__(self, openai_api_key: str):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key

    def generate_embeddings(self, thoughts: List[Dict]) -> np.ndarray:
        """Generate embeddings for thoughts"""
        texts = [thought['content'] for thought in thoughts]
        return self.embedding_model.encode(texts)

    def cluster_thoughts(self, embeddings: np.ndarray, eps: float = 0.3) -> List[int]:
        """Cluster similar thoughts using DBSCAN"""
        clustering = DBSCAN(eps=eps, min_samples=2).fit(embeddings)
        return clustering.labels_

    def identify_themes(self, thoughts: List[Dict], cluster_labels: List[int]) -> Dict[int, str]:
        """Identify themes for each cluster using GPT"""
        clusters = defaultdict(list)
        for thought, label in zip(thoughts, cluster_labels):
            if label != -1:  # Ignore noise points
                clusters[label].append(thought['content'])

        themes = {}
        for cluster_id, cluster_thoughts in clusters.items():
            prompt = f"""
            Analyze these related thoughts and identify the main theme:
            {'\n'.join(cluster_thoughts)}
            
            Provide a concise theme label (3-5 words).
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a thought analysis assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            themes[cluster_id] = response.choices[0].message.content.strip()

        return themes

    def generate_insights(self, thoughts: List[Dict], themes: Dict[int, str]) -> Dict[str, List[str]]:
        """Generate detailed insights and recommendations"""
        thoughts_text = "\n".join([t['content'] for t in thoughts])
        themes_text = "\n".join([f"Theme: {theme}" for theme in themes.values()])

        prompt = f"""
        Analyze these thoughts and their themes:

        Thoughts:
        {thoughts_text}

        Identified Themes:
        {themes_text}

        Provide analysis in the following categories:
        1. Key Patterns
        2. Knowledge Gaps
        3. Action Items
        4. Learning Opportunities
        5. Potential Connections

        For each category, provide 2-3 specific, actionable insights.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an analytical assistant specializing in pattern recognition and insight generation."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the response into structured insights
        raw_insights = response.choices[0].message.content
        return self._parse_insights(raw_insights)

    def _parse_insights(self, raw_insights: str) -> Dict[str, List[str]]:
        """Parse raw GPT response into structured insights"""
        categories = ['Key Patterns', 'Knowledge Gaps', 'Action Items', 
                     'Learning Opportunities', 'Potential Connections']
        parsed_insights = defaultdict(list)
        
        current_category = None
        for line in raw_insights.split('\n'):
            line = line.strip()
            if any(category in line for category in categories):
                current_category = line.split(':')[0].strip()
            elif line and current_category and '-' in line:
                parsed_insights[current_category].append(line.strip('- '))

        return dict(parsed_insights)

class EnhancedEveningReview:
    def __init__(self, thought_manager: ThoughtManager, voice_interface: VoiceInterface, 
                 analyzer: ThoughtAnalyzer):
        self.thought_manager = thought_manager
        self.voice_interface = voice_interface
        self.analyzer = analyzer

    def generate_review(self) -> str:
        """Generate comprehensive evening review"""
        thoughts = self.thought_manager.get_todays_thoughts()
        
        if not thoughts:
            return "No thoughts captured today."

        # Generate embeddings and cluster thoughts
        embeddings = self.analyzer.generate_embeddings(thoughts)
        cluster_labels = self.analyzer.cluster_thoughts(embeddings)
        
        # Identify themes
        themes = self.analyzer.identify_themes(thoughts, cluster_labels)
        
        # Generate detailed insights
        insights = self.analyzer.generate_insights(thoughts, themes)
        
        # Generate structured review text
        review = self._format_review(thoughts, themes, insights)
        return review

    def _format_review(self, thoughts: List[Dict], themes: Dict[int, str], 
                      insights: Dict[str, List[str]]) -> str:
        """Format the review in a structured, easy-to-follow manner"""
        review_parts = []

        # Overview
        review_parts.append("📋 Evening Thought Review\n")
        review_parts.append(f"Total thoughts captured today: {len(thoughts)}\n")

        # Themes
        review_parts.append("\n🎯 Main Themes Identified:")
        for theme_id, theme in themes.items():
            review_parts.append(f"• {theme}")

        # Detailed Insights
        review_parts.append("\n🔍 Analysis & Insights:")
        for category, category_insights in insights.items():
            review_parts.append(f"\n{category}:")
            for insight in category_insights:
                review_parts.append(f"• {insight}")

        # Timeline Review
        review_parts.append("\n⏰ Timeline of Thoughts:")
        sorted_thoughts = sorted(thoughts, key=lambda x: x['timestamp'])
        for thought in sorted_thoughts:
            timestamp = datetime.fromisoformat(thought['timestamp'])
            review_parts.append(f"[{timestamp.strftime('%H:%M')}] {thought['content']}")

        return "\n".join(review_parts)

    def deliver_review(self):
        """Deliver the review through voice and return text"""
        review_text = self.generate_review()
        
        # Split review into digestible chunks for voice delivery
        chunks = self._chunk_review(review_text)
        
        for chunk in chunks:
            self.voice_interface.speak(chunk)
            time.sleep(1)  # Pause between chunks
        
        return review_text

    def _chunk_review(self, review_text: str) -> List[str]:
        """Split review into appropriate chunks for voice delivery"""
        chunks = []
        current_chunk = []
        current_length = 0
        max_chunk_length = 200  # Adjust based on preferred chunk size

        for line in review_text.split('\n'):
            if current_length + len(line) > max_chunk_length:
                chunks.append(' '.join(current_chunk))
                current_chunk = [line]
                current_length = len(line)
            else:
                current_chunk.append(line)
                current_length += len(line)

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks
