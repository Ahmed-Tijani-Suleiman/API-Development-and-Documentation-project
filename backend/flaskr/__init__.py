import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    present_questions = questions[start:end]
    return present_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)


    #TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    CORS(app)
   
   #@TODO: Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        #select all categories
        categories = Category.query.all()
        
        if len(categories) == 0:
          abort(404)

        return jsonify({
       'success': True,
       'categories': {
          category.id: category.type for category in categories
              }
       })
    


    """""
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=['GET'])
    def get_questions():
        #select all questions and paginate
        selection = Question.query.order_by(Question.id).all()
        categories = Category.query.all()
        present_questions = paginate_questions(request, selection)
        

        if len(present_questions) == 0:
            abort(404)

        """
        This should return a list of questions,
        number of total questions, current category, categories.
        """
        return jsonify({
            'success': True,
            'questions': present_questions,
            'total_questions': len(selection),
            'current_category': "",
            'categories':  {
          category.id: category.type for category in categories
              },
        }), 200
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:id>", methods=['DELETE'])

    def delete_question(id):
        try:
            #select specific question to delete
          book = Question.query.filter(Question.id == id).one_or_none()

          if book is None:
              abort(404)

          book.delete()
          #return list of questions
          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)

          return jsonify({
            'success': True,
            'deleted': id,
            'books': current_questions,
            'total_books': len(Question.query.all())
      })

        except:
          abort(422)

        



    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        # get parameters to create new question
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        search_value = body.get('searchTerm')
        
    
        
        try:
            #search for string in questions
            if search_value != None:
                questions_list = Question.query.filter( Question.question.ilike('%'+search_value+'%')).all()
                if questions_list is None:
                   abort(404)
                else:
                    currentQuestions = paginate_questions(request, questions_list)
                    return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questions_list)
            })
            # create new question
            else:
                book = Question( question= new_question, answer= new_answer, difficulty=new_difficulty, category= new_category)
                book.insert()

                selection = Question.query.order_by(Question.id).all()
                current_question = paginate_questions(request, selection)

                return jsonify({
                'success': True,
                'created': book.id,
                'question': current_question,
                'total_question': len(Question.query.all())
      })

        except:
           abort(422)



    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_question_by_category(id):
        category = Category.query.get(id)
        if (category is None):
            abort(404)

        try:
        #get questions by category
           questions = Question.query.filter_by(category=category.id).all()
      
           current_questions = paginate_questions(request, questions)

           return jsonify({
        'success': True,
        'questions': current_questions,
        'current_category': category.type,
        'total_questions': len(questions)
      })
        except:
          abort(500)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():

        try:
            body = request.get_json()
            #get previous question
            previous_questions = body.get('previous_questions', [])
            #get quiz category
            quiz_category = body.get('quiz_category', None)
            category_id = quiz_category['id']
            
            #Return all questions
            if category_id == 0:
                questions = Question.query.all()
                
            else:
                questions = Question.query.filter(Question.category == category_id).all()
                
            new_questions=[]
            for question in questions:
                if question.id not in previous_questions:
                    new_questions.append(question)
            
            question = random.choice(new_questions)
        
            return jsonify({
                'success': True,
                'question': question.format()
            })

        except Exception as e:
            print(e)
            abort(404)




    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Page not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_recource(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable recource"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    @app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "Invalid method!"
        }), 405

    return app

