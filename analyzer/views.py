# analyzer/views.py
import re
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import StringRecord
from .serializers import StringRecordSerializer
from .utils import analyze_string
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class StringListCreateView(ListCreateAPIView):
    """
    POST /api/strings → Analyze and store a string.
    GET /api/strings → Retrieve all analyzed strings.
    """
    serializer_class = StringRecordSerializer
    queryset = StringRecord.objects.all()
    applied_filters = {}

    @swagger_auto_schema(
        operation_summary="Retrieve all analyzed strings",
        operation_description="Returns a list of all analyzed strings stored in the system.",
        responses={200: StringRecordSerializer(many=True)}
    )
    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        self.applied_filters = {}

        try:
            if "is_palindrome" in params:
                v = params.get("is_palindrome").lower()
                if v not in ("true", "false"):
                    raise ValidationError("is_palindrome must be 'true' or 'false'")
                qs = qs.filter(is_palindrome=(v == "true"))
                self.applied_filters["is_palindrome"] = (v == "true")

            if "min_length" in params:
                min_len = int(params.get("min_length"))
                qs = qs.filter(length__gte=min_len)
                self.applied_filters["min_length"] = min_len

            if "max_length" in params:
                max_len = int(params.get("max_length"))
                qs = qs.filter(length__lte=max_len)
                self.applied_filters["max_length"] = max_len

            if "word_count" in params:
                wc = int(params.get("word_count"))
                qs = qs.filter(word_count=wc)
                self.applied_filters["word_count"] = wc

            if "contains_character" in params:
                char = params.get("contains_character")
                if len(char) != 1:
                    raise ValidationError("contains_character must be a single character")
                qs = qs.filter(value__icontains=char)
                self.applied_filters["contains_character"] = char

            return qs
        except ValueError:
            raise ValidationError("Invalid query parameter values or types")

    # ✅ Override list to include filters_applied
    @swagger_auto_schema(
        operation_summary="Retrieve all analyzed strings",
        operation_description="Returns a list of all analyzed strings stored in the system.",
        responses={200: StringRecordSerializer(many=True)},
        operation_id="strings_list"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "data": serializer.data,
            "count": queryset.count(),
            "filters_applied": self.applied_filters
        })

    # Keep your existing create() method as-is
    @swagger_auto_schema(
        operation_summary="Create and analyze a new string",
        operation_description=(
            "This endpoint accepts a string input, analyzes it to compute properties "
            "such as length, palindrome status, unique characters, word count, and "
            "SHA256 hash. The analyzed string and its metadata are stored in the database."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'value': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The string to analyze',
                    example='hello'
                ),
            },
            required=['value']
        ),
        responses={
            201: openapi.Response(description="String analyzed and stored successfully"),
            400: "Invalid request body",
            409: "Duplicate string",
            422: "Invalid data type",
        },
        operation_id="strings_create"
       
    )
    def create(self, request, *args, **kwargs):
        value = request.data.get("value", None)

        if value is None or (isinstance(value, str) and value.strip() == ""):
            return Response(
                {"error": "Invalid request body or missing 'value' field"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(value, str):
            return Response(
                {"error": "Invalid data type for 'value' (must be string)"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        props = analyze_string(value)
        sha = props["sha256_hash"]

        if StringRecord.objects.filter(id=sha).exists() or StringRecord.objects.filter(value=value).exists():
            return Response(
                {"error": "String already exists in the system"},
                status=status.HTTP_409_CONFLICT
            )

        record = StringRecord.objects.create(
            id=sha,
            value=value,
            length=props["length"],
            is_palindrome=props["is_palindrome"],
            unique_characters=props["unique_characters"],
            word_count=props["word_count"],
            sha256_hash=props["sha256_hash"],
            character_frequency_map=props["character_frequency_map"],
        )

        data = {
            "id": record.id,
            "value": record.value,
            "properties": props,
            "created_at": record.created_at.isoformat().replace("+00:00", "Z"),
        }
        return Response(data, status=status.HTTP_201_CREATED)


class StringDetailView(APIView):
    def get(self, request, string_value):
        record = StringRecord.objects.filter(value=string_value).first()
        if not record:
            return Response(
                {"error": "String does not exist in the system"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StringRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, string_value):
        record = StringRecord.objects.filter(value=string_value).first()
        if not record:
            return Response(
                {"error": "String does not exist in the system"},
                status=status.HTTP_404_NOT_FOUND
            )
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NaturalLanguageFilterView(APIView):

    @swagger_auto_schema(
        operation_summary="Filter strings using natural language",
        manual_parameters=[
            openapi.Parameter(
                'query', openapi.IN_QUERY,
                description="Natural language filter, e.g. 'palindromic, longer than 5, letter a'",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: openapi.Response(description="Filtered string records")},
        operation_id="strings_filter_by_natural_language"
    )
    def get(self, request):
        query = request.query_params.get("query", "")
        if not query or not query.strip():
            return Response({"error": "Query is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        parsed = {}
        ql = query.lower()

        if "palindromic" in ql:
            parsed["is_palindrome"] = True
        if "single word" in ql or "one word" in ql:
            parsed["word_count"] = 1
        if m := re.search(r"longer than (\d+)", ql):
            parsed["min_length"] = int(m.group(1)) + 1
        if m := re.search(r"shorter than (\d+)", ql):
            parsed["max_length"] = int(m.group(1)) - 1
        if m := re.search(r"letter ([a-z])", ql):
            parsed["contains_character"] = m.group(1)

        if not parsed:
            return Response(
                {"error": "Unable to parse natural language query"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Conflicting filters check
        if parsed.get("min_length") and parsed.get("max_length") and parsed["min_length"] > parsed["max_length"]:
            return Response(
                {"error": "Query parsed but resulted in conflicting filters"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        qs = StringRecord.objects.all()
        if parsed.get("is_palindrome"):
            qs = qs.filter(is_palindrome=True)
        if parsed.get("word_count"):
            qs = qs.filter(word_count=parsed["word_count"])
        if parsed.get("min_length"):
            qs = qs.filter(length__gte=parsed["min_length"])
        if parsed.get("max_length"):
            qs = qs.filter(length__lte=parsed["max_length"])
        if parsed.get("contains_character"):
            qs = qs.filter(value__icontains=parsed["contains_character"])

        serializer = StringRecordSerializer(qs, many=True)
        return Response({
            "data": serializer.data,
            "count": qs.count(),
            "interpreted_query": {
                "original": query,
                "parsed_filters": parsed
            }
        }, status=status.HTTP_200_OK)
