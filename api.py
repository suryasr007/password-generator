from flask import Flask, jsonify, abort, render_template, request
from flask_restful import Resource, Api, reqparse
from webargs import fields, validate
from webargs.flaskparser import use_args
from password_generator import PasswordGenerator
import re

app = Flask(__name__)
api = Api(app, prefix="/api/v1")

parser = reqparse.RequestParser()

'''
Defaults
self.minlen = 6
self.maxlen = 16
self.minuchars = 1
self.minlchars = 1
self.minnumbers = 1
self.minschars = 1
self.excludeuchars = ""
self.excludelchars = ""
self.excludenumbers = ""
self.excludeschars = ""
'''

pwg = PasswordGenerator()

password_generator_args = {
    'minlen': fields.Int(missing=6, validate=lambda val: val > 0),
    'maxlen': fields.Int(missing=16, validate=lambda val: val > 0),
    'minuchars': fields.Int(missing=1, validate=lambda val: val > 0),
    'minuchars': fields.Int(missing=1, validate=lambda val: val > 0),
    'minlchars': fields.Int(missing=1, validate=lambda val: val > 0),
    'excludeuchars': fields.Str(missing=''),
    'excludelchars': fields.Str(missing=''),
    'excludenumbers': fields.Str(missing=''),
    'excludeschars': fields.Str(missing='')
}

shuffle_password_args = {
    'maxlen': fields.Int(required={'message': 'maximum length required', 'code': 400}),
    'password': fields.Str(required={'message': 'Password required', 'code': 400})
}

non_duplicate_args = {
    'maxlen': fields.Int(required={'message': 'maximum length required', 'code': 400})
}


class PasswordGenerator(Resource):

    @use_args(password_generator_args)
    def get(self, args):
        try:
            pwg.__dict__.update(args)
            res = pwg.generate()
        except Exception as e:
            abort(404, str(e))

        return jsonify({'password': res})


class ShufflePassword(Resource):

    @use_args(shuffle_password_args)
    def get(self, args):
        try:
            res = pwg.shuffle_password(password=args["password"], maxlen=args["maxlen"])
        except Exception as e:
            abort(404, str(e))

        return jsonify({'password': res})


class NonDuplicatePassword(Resource):

    @use_args(non_duplicate_args)
    def get(self, args):
        try:
            res = pwg.non_duplicate_password(maxlen=args["maxlen"])
        except Exception as e:
            abort(404, str(e))

        return jsonify({'password': res})


@app.route('/', methods=["GET", "POST"])
def home():

    if request.method == "GET":
        return render_template("home.html",
                               minlen=6,
                               maxlen=16,
                               minuchars=1,
                               minlchars=1,
                               minnumbers=1,
                               minschars=1
                               )

    # Check for generate = 1
    if not int(request.form.get("generate")) == 1:
        return "Something went wrong :( Try pressing the button again"

    # Check for chars to be excluded
    if not request.form.get("excludechars") == "":
        excludechars = request.form.get("excludechars")
        lowertoexclude = ""
        uppertoexclude = ""
        numberstoexclude = ""
        specialtoexclude = ""
        for c in range(0, len(excludechars)):
            if re.match("^[a-z]", excludechars[c]):
                lowertoexclude += excludechars[c]
            elif re.match("^[A-Z]", excludechars[c]):
                uppertoexclude += excludechars[c]
            elif re.match("^[0-9]", excludechars[c]):
                numberstoexclude += excludechars[c]
            elif not re.match("^[a-zA-Z0-9_]*$", excludechars[c]):
                specialtoexclude += excludechars[c]

        pwg.excludelchars = lowertoexclude
        pwg.excludeuchars = uppertoexclude
        pwg.excludenumbers = numberstoexclude
        pwg.excludeschars = specialtoexclude

    # Set pwg args
    pwg.minlen = int(request.form.get("minlen"))
    pwg.maxlen = int(request.form.get("maxlen"))
    pwg.minuchars = int(request.form.get("minuchars"))
    pwg.minlchars = int(request.form.get("minlchars"))
    pwg.minnumbers = int(request.form.get("minnumbers"))
    pwg.minschars = int(request.form.get("minschars"))

    # Generate password
    pwd = pwg.generate()

    return render_template("home.html",
                           pwd=pwd,
                           minlen=request.form.get("minlen"),
                           maxlen=request.form.get("maxlen"),
                           minuchars=request.form.get("minuchars"),
                           minlchars=request.form.get("minlchars"),
                           minnumbers=request.form.get("minnumbers"),
                           minschars=request.form.get("minschars"),
                           excludechars=request.form.get("excludechars")
                           )


api.add_resource(PasswordGenerator, '/generate')
api.add_resource(ShufflePassword, '/shuffle')
api.add_resource(NonDuplicatePassword, '/nonduplicate')

if __name__ == '__main__':
    app.run()
