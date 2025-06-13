# BE/medical/views/knowledge.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters  # Add this line
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from ..models import MedicalCondition, Symptom, ConditionSymptom, SpecialistRecommendation
from ..serializers.analysis import SymptomAnalysisSerializer, MedicalConditionSerializer
from ..services.enhanced_analyzer import EnhancedSymptomAnalyzer


class SymptomAnalysisView(APIView):
    """
    Analyze user symptoms and return possible conditions with recommendations
    """
    def post(self, request):
        serializer = SymptomAnalysisSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Simple keyword-based analysis
            results = self.analyze_symptoms(data)

            return Response(results, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def analyze_symptoms(self, data):
        """
        Analyze symptoms and return recommendations
        """
        primary_symptoms = data.get('primary_symptoms', [])
        severity = data.get('severity', 5)
        duration = data.get('duration', '')
        additional_symptoms = data.get('additional_symptoms', [])

        # Get all symptoms from database
        all_symptoms = ' '.join(primary_symptoms + additional_symptoms).lower()

        # Find matching conditions
        conditions_scores = {}
        conditions = MedicalCondition.objects.all()

        for condition in conditions:
            score = 0
            condition_symptoms = ConditionSymptom.objects.filter(condition=condition)

            for cs in condition_symptoms:
                if cs.symptom.name.lower() in all_symptoms:
                    score += cs.probability
                    if cs.is_primary:
                        score += 0.2  # Bonus for primary symptoms

            # Severity adjustment
            if severity >= 7:
                score += 0.1

            if score > 0:
                conditions_scores[condition] = score

        # Sort by score
        sorted_conditions = sorted(conditions_scores.items(), key=lambda x: x[1], reverse=True)

        if not sorted_conditions:
            return {
                'most_likely': None,
                'confidence': 0,
                'recommendations': [{
                    'specialist': 'General Practitioner',
                    'urgency': 'MEDIUM',
                    'notes': 'Please consult a doctor for proper diagnosis'
                }]
            }

        # Get top condition
        top_condition, confidence = sorted_conditions[0]

        # Get recommendations for top condition
        recommendations = SpecialistRecommendation.objects.filter(condition=top_condition)

        return {
            'most_likely': {
                'name': top_condition.name,
                'description': top_condition.description,
                'severity': top_condition.severity_level
            },
            'confidence': min(confidence, 1.0),
            'recommendations': [
                {
                    'specialist': rec.specialist_type,
                    'urgency': rec.urgency_level,
                    'notes': rec.notes
                } for rec in recommendations
            ],
            'all_matches': [
                {
                    'name': condition.name,
                    'confidence': min(score, 1.0)
                } for condition, score in sorted_conditions[:3]
            ]
        }

class MedicalKnowledgeView(APIView):
    """
    Get medical knowledge base data
    """
    def get(self, request):
        conditions = MedicalCondition.objects.all()
        symptoms = Symptom.objects.all()

        return Response({
            'conditions': MedicalConditionSerializer(conditions, many=True).data,
            'common_symptoms': [s.name for s in symptoms.filter(is_common=True)]
        })



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class MedicalConditionsListView(ListAPIView):
    """
    List all medical conditions with filtering and search
    """
    serializer_class = MedicalConditionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'severity_level']
    ordering = ['name']

    def get_queryset(self):
        queryset = MedicalCondition.objects.all()

        # Filter by severity level
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity_level=severity.upper())

        # Filter by symptom
        symptom = self.request.query_params.get('symptom')
        if symptom:
            queryset = queryset.filter(
                conditionsymptom__symptom__name__icontains=symptom
            ).distinct()

        return queryset

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request, *args, **kwargs):
        """Override to add caching"""
        return super().get(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """Override to add metadata"""
        response = super().list(request, *args, **kwargs)

        # Add metadata
        response.data['metadata'] = {
            'total_conditions': MedicalCondition.objects.count(),
            'severity_levels': [
                {'level': 'MILD', 'count': MedicalCondition.objects.filter(severity_level='MILD').count()},
                {'level': 'MODERATE', 'count': MedicalCondition.objects.filter(severity_level='MODERATE').count()},
                {'level': 'SEVERE', 'count': MedicalCondition.objects.filter(severity_level='SEVERE').count()},
            ]
        }

        return response


class MedicalConditionDetailView(APIView):
    """
    Get detailed information about a specific medical condition
    """

    @method_decorator(cache_page(60 * 30))  # Cache for 30 minutes
    def get(self, request, condition_key):
        """
        Get detailed condition information

        URL: /api/medical/conditions/flu/
        """
        try:
            # Try to get from knowledge base first
            analyzer = EnhancedSymptomAnalyzer()
            kb_conditions = analyzer.knowledge_base.get('conditions', {})

            if condition_key in kb_conditions:
                condition_data = kb_conditions[condition_key]

                # Get additional data from database if available
                try:
                    db_condition = MedicalCondition.objects.get(
                        name__iexact=condition_data['name']
                    )

                    # Get related symptoms
                    related_symptoms = ConditionSymptom.objects.filter(
                        condition=db_condition
                    ).select_related('symptom')

                    # Get specialist recommendations
                    recommendations = SpecialistRecommendation.objects.filter(
                        condition=db_condition
                    )

                    # Build comprehensive response
                    response_data = {
                        'key': condition_key,
                        'name': condition_data['name'],
                        'description': condition_data['description'],
                        'severity_level': condition_data['severity_level'],
                        'primary_symptoms': condition_data.get('symptoms', []),
                        'sources': condition_data.get('sources', []),
                        'detailed_symptoms': [
                            {
                                'name': cs.symptom.name,
                                'probability': cs.probability,
                                'is_primary': cs.is_primary,
                                'description': cs.symptom.description
                            }
                            for cs in related_symptoms
                        ],
                        'specialist_recommendations': [
                            {
                                'specialist': rec.specialist_type,
                                'urgency': rec.urgency_level,
                                'notes': rec.notes
                            }
                            for rec in recommendations
                        ],
                        'probability_data': analyzer.probability_matrix.get(condition_key, {}),
                        'differential_diagnosis': self.get_differential_conditions(condition_key, analyzer),
                        'metadata': {
                            'last_updated': db_condition.updated_at.isoformat() if hasattr(db_condition, 'updated_at') else None,
                            'data_source': 'database_enhanced'
                        }
                    }

                except MedicalCondition.DoesNotExist:
                    # Use knowledge base data only
                    response_data = {
                        'key': condition_key,
                        'name': condition_data['name'],
                        'description': condition_data['description'],
                        'severity_level': condition_data['severity_level'],
                        'primary_symptoms': condition_data.get('symptoms', []),
                        'sources': condition_data.get('sources', []),
                        'probability_data': analyzer.probability_matrix.get(condition_key, {}),
                        'differential_diagnosis': self.get_differential_conditions(condition_key, analyzer),
                        'metadata': {
                            'data_source': 'knowledge_base_only'
                        }
                    }

                return Response(response_data)

            else:
                return Response({
                    'error': 'Condition not found',
                    'message': f'Condition "{condition_key}" not found in knowledge base',
                    'available_conditions': list(kb_conditions.keys())
                }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Condition detail error: {e}")
            return Response({
                'error': 'Unable to retrieve condition details',
                'message': 'Please try again later'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_differential_conditions(self, condition_key, analyzer):
        """Get conditions that are similar for differential diagnosis"""
        try:
            current_symptoms = set(analyzer.probability_matrix.get(condition_key, {}).keys())
            differential_conditions = []

            for other_key, other_probs in analyzer.probability_matrix.items():
                if other_key != condition_key:
                    other_symptoms = set(other_probs.keys())

                    # Calculate symptom overlap
                    overlap = current_symptoms.intersection(other_symptoms)
                    if len(overlap) >= 2:  # At least 2 shared symptoms
                        overlap_percentage = len(overlap) / len(current_symptoms.union(other_symptoms))

                        differential_conditions.append({
                            'condition_key': other_key,
                            'condition_name': analyzer.knowledge_base['conditions'][other_key]['name'],
                            'shared_symptoms': list(overlap),
                            'overlap_percentage': round(overlap_percentage, 2)
                        })

            # Sort by overlap percentage
            return sorted(differential_conditions, key=lambda x: x['overlap_percentage'], reverse=True)[:3]

        except Exception as e:
            logger.error(f"Differential diagnosis error: {e}")
            return []


class SymptomSearchView(APIView):
    """
    Search for symptoms with fuzzy matching and suggestions
    """

    def get(self, request):
        """
        Search symptoms with query parameter

        URL: /api/medical/symptoms/search/?q=fever&limit=10
        """
        try:
            query = request.query_params.get('q', '').strip()
            limit = min(int(request.query_params.get('limit', 10)), 50)

            if not query:
                return Response({
                    'error': 'Query parameter "q" is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            if len(query) < 2:
                return Response({
                    'error': 'Query must be at least 2 characters long'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Search in database
            db_symptoms = self.search_database_symptoms(query, limit)

            # Search in knowledge base
            kb_symptoms = self.search_knowledge_base_symptoms(query, limit)

            # Combine and deduplicate results
            all_symptoms = self.combine_symptom_results(db_symptoms, kb_symptoms, limit)

            return Response({
                'query': query,
                'results': all_symptoms,
                'total_found': len(all_symptoms),
                'suggestions': self.get_search_suggestions(query) if len(all_symptoms) < 3 else []
            })

        except ValueError:
            return Response({
                'error': 'Invalid limit parameter'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Symptom search error: {e}")
            return Response({
                'error': 'Search failed',
                'message': 'Please try again with different search terms'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def search_database_symptoms(self, query, limit):
        """Search symptoms in database"""
        try:
            symptoms = Symptom.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            ).distinct()[:limit]

            return [
                {
                    'name': symptom.name,
                    'description': symptom.description,
                    'is_common': getattr(symptom, 'is_common', False),
                    'related_conditions': [
                        cs.condition.name for cs in ConditionSymptom.objects.filter(
                            symptom=symptom
                        ).select_related('condition')[:3]
                    ],
                    'source': 'database',
                    'match_type': 'exact' if query.lower() in symptom.name.lower() else 'partial'
                }
                for symptom in symptoms
            ]
        except Exception as e:
            logger.error(f"Database symptom search error: {e}")
            return []

    def search_knowledge_base_symptoms(self, query, limit):
        """Search symptoms in knowledge base"""
        try:
            analyzer = EnhancedSymptomAnalyzer()
            symptoms_index = analyzer.symptoms_index or {}

            query_lower = query.lower()
            matching_symptoms = []

            for symptom_name, symptom_data in symptoms_index.items():
                if query_lower in symptom_name.lower():
                    matching_symptoms.append({
                        'name': symptom_name,
                        'description': f"Symptom related to {', '.join(symptom_data.get('conditions', []))}",
                        'frequency': symptom_data.get('frequency', 0),
                        'related_conditions': symptom_data.get('conditions', []),
                        'source': 'knowledge_base',
                        'match_type': 'exact' if query_lower == symptom_name.lower() else 'partial'
                    })

            # Sort by frequency and match type
            matching_symptoms.sort(key=lambda x: (x['match_type'] == 'exact', x['frequency']), reverse=True)

            return matching_symptoms[:limit]

        except Exception as e:
            logger.error(f"Knowledge base symptom search error: {e}")
            return []

    def combine_symptom_results(self, db_symptoms, kb_symptoms, limit):
        """Combine and deduplicate symptom results"""
        combined = {}

        # Add database symptoms
        for symptom in db_symptoms:
            key = symptom['name'].lower()
            combined[key] = symptom

        # Add knowledge base symptoms (don't overwrite database results)
        for symptom in kb_symptoms:
            key = symptom['name'].lower()
            if key not in combined:
                combined[key] = symptom

        # Sort by relevance and return top results
        results = list(combined.values())
        results.sort(key=lambda x: (x['match_type'] == 'exact', x.get('frequency', 0)), reverse=True)

        return results[:limit]

    def get_search_suggestions(self, query):
        """Get search suggestions for low-result queries"""
        suggestions = []

        # Common symptom suggestions based on partial matches
        common_symptoms = [
            'fever', 'headache', 'cough', 'sore throat', 'runny nose',
            'body aches', 'fatigue', 'nausea', 'dizziness', 'chest pain',
            'shortness of breath', 'sneezing', 'congestion', 'chills'
        ]

        query_lower = query.lower()

        for symptom in common_symptoms:
            if query_lower in symptom or symptom.startswith(query_lower):
                suggestions.append(symptom)

        return suggestions[:5]