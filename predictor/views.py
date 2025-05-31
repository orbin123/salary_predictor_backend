from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SalaryInputSerializer
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
import json

# Load model
model = joblib.load('Salary_predictor.pkl')

class PredictSalaryAPIView(APIView):
    def post(self, request):
        try:
            print("Received data:", request.data)  # Debug print
            serializer = SalaryInputSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid input', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            input_data = serializer.validated_data
            features = [input_data[f"feature{i+1}"] for i in range(10)]
            print("Features values:", features)  # Debug print
            
            column_names = ["Leetcode_completed", "Project_1_score", "Project_2_score", 
                          "Project_3_score", "Total_full_stack_projects", "Years_of_experience", 
                          "No_of_certifications", "CGPA", "Non_IT_student", "Communication_Level"]
            
            df = pd.DataFrame([features], columns=column_names)
            print("DataFrame:", df)  # Debug print

            # Create 'experience' category
            def map_experience(years):
                try:
                    years = float(years)
                    if years <= 0.5:
                        return 'fresher'
                    elif years <= 1:
                        return 'mid-junior'
                    elif years <= 1.5:
                        return 'junior'
                    else:
                        return 'mid-senior'
                except (ValueError, TypeError) as e:
                    print(f"Error converting years to float: {e}")  # Debug print
                    return 'fresher'  # default value

            try:
                # Ensure communication level is lowercase
                df['Communication_Level'] = df['Communication_Level'].str.lower()
                
                # Map experience
                df['Experience'] = df['Years_of_experience'].apply(map_experience)
                df['No_of_certificationsXCGPA'] = pd.to_numeric(df['No_of_certifications']) * pd.to_numeric(df['CGPA'])

                # Calculate average of project scores
                project_scores = [
                    float(df.iloc[0]['Project_1_score']),
                    float(df.iloc[0]['Project_2_score']),
                    float(df.iloc[0]['Project_3_score'])
                ]
                df['Average_of_Project_score'] = sum(project_scores) / 3

                # Define categories and ensure they're lowercase
                comm_categories = [['beginner', 'fluent', 'expert', 'exceptional']]
                exp_categories = [['fresher', 'mid-junior', 'junior', 'mid-senior']]
                
                encoder1 = OrdinalEncoder(categories=comm_categories)
                encoder2 = OrdinalEncoder(categories=exp_categories)
                
                df['Communication_Level_encoded'] = encoder1.fit_transform(df[['Communication_Level']])
                df['Experience_Category_encoded'] = encoder2.fit_transform(df[['Experience']])

                X = df.drop(columns=['Communication_Level', 'Experience'])
                
                prediction = model.predict(X)
                predict_value = prediction[0]//100
                return Response({"salary": float(predict_value)})
                
            except Exception as e:
                print(f"Error during prediction: {str(e)}")  # Debug print
                return Response(
                    {'error': 'Prediction failed', 'details': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            print(f"Error in view: {str(e)}")  # Debug print
            return Response(
                {'error': 'Server error', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )