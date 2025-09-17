"""Run this package like a tiny app."""  # This top line is a note for humans (a docstring) that explains the file.

from .main import main  # We import the main() function that starts the program.

# The next two lines make sure this only runs when you start the program directly.
if __name__ == "__main__":  # If this file is the one Python runs first...
    main()  # ...then call main() to launch the Car Rental app.
