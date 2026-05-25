"""
Comprehensive lesson content generator for Brain Buddy
Generates 22 distinct educational lessons following age-specific requirements
"""

def get_lesson_content(subject, topic_id):
    """
    Get detailed lesson content for specific topics
    Returns authentic educational content with activities, examples, and practice questions
    """
    
    lesson_library = {
        'maths': {
            'numbers-to-20': {
                'lessons': [
                    {
                        'id': 'count-animals',
                        'title': 'Count the Animals',
                        'difficulty': 'easy',
                        'explanation': "Look at the farm! How many animals can you count?",
                        'activity': "Count all the cows in the picture.",
                        'example': "Student types '5' or taps a '5' button.",
                        'practice': "Count all the cows in the picture.",
                        'visual_aid': "Image of 5 cartoon cows.",
                        'interactive_elements': ['animal_counting', 'number_input', 'farm_scene']
                    },
                    {
                        'id': 'number-recognition-5',
                        'title': 'Number Recognition to 5',
                        'difficulty': 'easy',
                        'explanation': "Which number matches the dots?",
                        'activity': "Tap the number that shows how many dots there are.",
                        'example': "Student taps '3'.",
                        'practice': "Tap the number that shows how many dots there are.",
                        'visual_aid': "Image of 3 dots and three number options: 2, 3, 4.",
                        'interactive_elements': ['dot_counting', 'number_matching', 'multiple_choice']
                    },
                    {
                        'id': 'counting-fingers',
                        'title': 'Counting Fingers',
                        'difficulty': 'easy',
                        'explanation': "Use your fingers to help you count!",
                        'activity': "Show 4 fingers. Now, how many fingers do you see in the picture?",
                        'example': "Student types '4'.",
                        'practice': "Show 4 fingers. Now, how many fingers do you see in the picture?",
                        'visual_aid': "Image of a hand showing 4 fingers.",
                        'interactive_elements': ['finger_counting', 'hand_visual', 'number_input']
                    },
                    {
                        'id': 'counting-mixed-objects',
                        'title': 'Counting Objects (Mixed)',
                        'difficulty': 'easy',
                        'explanation': "Let's count all the different toys in the basket.",
                        'activity': "Count how many toys are in the basket.",
                        'example': "Student types '6'.",
                        'practice': "Count how many toys are in the basket.",
                        'visual_aid': "Image of a basket with 6 mixed toys (e.g., ball, doll, car).",
                        'interactive_elements': ['object_counting', 'mixed_items', 'basket_visual']
                    },
                    {
                        'id': 'number-before',
                        'title': 'Number Before (to 10)',
                        'difficulty': 'easy',
                        'explanation': "What number comes just before this one?",
                        'activity': "Type the number that comes before 7.",
                        'example': "Student types '6'.",
                        'practice': "Type the number that comes before 7.",
                        'visual_aid': "Large numeral '7'.",
                        'interactive_elements': ['sequence_learning', 'number_input', 'large_numeral']
                    },
                    {
                        'id': 'number-after',
                        'title': 'Number After (to 10)',
                        'difficulty': 'easy',
                        'explanation': "What number comes right after this one?",
                        'activity': "Type the number that comes after 9.",
                        'example': "Student types '10'.",
                        'practice': "Type the number that comes after 9.",
                        'visual_aid': "Large numeral '9'.",
                        'interactive_elements': ['sequence_learning', 'number_input', 'large_numeral']
                    },
                    {
                        'id': 'counting-on',
                        'title': 'Counting On from a Number',
                        'difficulty': 'easy',
                        'explanation': "Start at 5 and count on 3 more jumps!",
                        'activity': "What number do you land on?",
                        'example': "Student types '8'.",
                        'practice': "What number do you land on?",
                        'visual_aid': "Number line from 0-10 with an arrow starting at 5 and jumping 3 times.",
                        'interactive_elements': ['number_line', 'counting_jumps', 'visual_arrows']
                    },
                    {
                        'id': 'counting-backwards',
                        'title': 'Counting Backwards (from 10)',
                        'difficulty': 'easy',
                        'explanation': "Let's count backwards like a rocket launch!",
                        'activity': "What number comes before 5 when counting backwards from 10?",
                        'example': "Student types '4'.",
                        'practice': "What number comes before 5 when counting backwards from 10?",
                        'visual_aid': "Rocket countdown from 10.",
                        'interactive_elements': ['countdown_visual', 'rocket_theme', 'backwards_counting']
                    },
                    {
                        'id': 'number-words-match',
                        'title': 'Matching Number Words to Numerals (to 10)',
                        'difficulty': 'easy',
                        'explanation': "Draw a line from the word to the correct number.",
                        'activity': "Match 'four' to the numeral 4.",
                        'example': "Student drags 'four' to '4'.",
                        'practice': "Match 'four' to the numeral 4.",
                        'visual_aid': "Two columns: one with number words (one, two, three, four), one with numerals (4, 1, 3, 2).",
                        'interactive_elements': ['drag_drop', 'word_matching', 'two_columns']
                    },
                    {
                        'id': 'ordinal-numbers',
                        'title': 'Ordinal Numbers (First, Second, Third)',
                        'difficulty': 'easy',
                        'explanation': "Who finished first in the race?",
                        'activity': "Click on the animal that is in the 'second' position.",
                        'example': "Student taps the animal with '2nd' label.",
                        'practice': "Click on the animal that is in the 'second' position.",
                        'visual_aid': "Image of 3 animals in a line, with '1st', '2nd', '3rd' labels.",
                        'interactive_elements': ['ordinal_positions', 'animal_race', 'position_labels']
                    },
                    {
                        'id': 'counting-2s',
                        'title': 'Counting in 2s (Introduction)',
                        'difficulty': 'easy',
                        'explanation': "Let's count the shoes! We can count them by 2s.",
                        'activity': "Count in 2s: 2, 4, 6, ____, 10.",
                        'example': "Student types '8'.",
                        'practice': "Count in 2s: 2, 4, 6, ____, 10.",
                        'visual_aid': "Image of 5 pairs of shoes.",
                        'interactive_elements': ['skip_counting', 'shoe_pairs', 'pattern_completion']
                    },
                    {
                        'id': 'counting-5s',
                        'title': 'Counting in 5s (Introduction)',
                        'difficulty': 'easy',
                        'explanation': "Look at the stars on these flags. Each flag has 5 stars. Let's count them in 5s!",
                        'activity': "Count in 5s: 5, 10, ____, 20.",
                        'example': "Student types '15'.",
                        'practice': "Count in 5s: 5, 10, ____, 20.",
                        'visual_aid': "Image of 4 flags, each with 5 stars.",
                        'interactive_elements': ['skip_counting', 'flag_visual', 'star_counting']
                    },
                    {
                        'id': 'counting-10s',
                        'title': 'Counting in 10s (Introduction)',
                        'difficulty': 'easy',
                        'explanation': "These are bundles of 10 sticks. Let's count them in 10s!",
                        'activity': "Count in 10s: 10, 20, 30, ____, 50.",
                        'example': "Student types '40'.",
                        'practice': "Count in 10s: 10, 20, 30, ____, 50.",
                        'visual_aid': "Image of 5 bundles of 10 sticks.",
                        'interactive_elements': ['skip_counting', 'stick_bundles', 'tens_visual']
                    },
                    {
                        'id': 'number-line-missing',
                        'title': 'Number Line Missing Numbers (to 10)',
                        'difficulty': 'easy',
                        'explanation': "Some numbers are missing from this number line. Can you fill them in?",
                        'activity': "Drag the correct numbers to fill the gaps: 1, 2, ___, 4, ___.",
                        'example': "Student drags '3' and '5' to the correct spots.",
                        'practice': "Drag the correct numbers to fill the gaps: 1, 2, ___, 4, ___.",
                        'visual_aid': "Number line 1-5 with two blanks.",
                        'interactive_elements': ['drag_drop', 'number_line', 'missing_numbers']
                    },
                    {
                        'id': 'grouping-objects',
                        'title': 'Grouping Objects (Introduction to place value)',
                        'difficulty': 'medium',
                        'explanation': "Let's put these items into groups of ten.",
                        'activity': "Count out 10 flowers and circle them. How many groups of 10 can you make?",
                        'example': "Student draws a circle around 10 flowers, then types '1' (group of 10).",
                        'practice': "Count out 10 flowers and circle them. How many groups of 10 can you make?",
                        'visual_aid': "Image of 15 scattered flowers.",
                        'interactive_elements': ['grouping_activity', 'circle_drawing', 'place_value_intro']
                    },
                    {
                        'id': 'comparing-more-less',
                        'title': 'Comparing Numbers (More/Less to 10)',
                        'difficulty': 'easy',
                        'explanation': "Which group has more apples?",
                        'activity': "Click on the basket with more apples.",
                        'example': "Student taps the basket with 7 apples.",
                        'practice': "Click on the basket with more apples.",
                        'visual_aid': "Image of two baskets: one with 7 apples, one with 4 apples.",
                        'interactive_elements': ['comparison', 'basket_visual', 'apple_counting']
                    },
                    {
                        'id': 'ordering-smallest-largest',
                        'title': 'Ordering Numbers (Smallest to Largest to 10)',
                        'difficulty': 'easy',
                        'explanation': "Put these numbers in order, starting from the smallest.",
                        'activity': "Drag the numbers 5, 2, 8 into the correct order.",
                        'example': "Student drags blocks to form '2, 5, 8'.",
                        'practice': "Drag the numbers 5, 2, 8 into the correct order.",
                        'visual_aid': "Three number blocks: 5, 2, 8.",
                        'interactive_elements': ['drag_drop', 'ordering', 'number_blocks']
                    },
                    {
                        'id': 'tally-marks',
                        'title': 'Tally Marks (Introduction)',
                        'difficulty': 'easy',
                        'explanation': "Tally marks help us count quickly! Each group of four with a line through is 5.",
                        'activity': "How many butterflies are shown with tally marks?",
                        'example': "Student types '7'.",
                        'practice': "How many butterflies are shown with tally marks?",
                        'visual_aid': "Image of tally marks for 7 butterflies (IIII II).",
                        'interactive_elements': ['tally_counting', 'butterfly_theme', 'tally_visual']
                    },
                    {
                        'id': 'teen-numbers',
                        'title': 'Counting on from a Teen Number',
                        'difficulty': 'easy',
                        'explanation': "Let's count on from 14.",
                        'activity': "What are the next two numbers after 14?",
                        'example': "Student types '15, 16'.",
                        'practice': "What are the next two numbers after 14?",
                        'visual_aid': "Numeral '14' and two empty boxes.",
                        'interactive_elements': ['teen_counting', 'sequence_building', 'number_input']
                    },
                    {
                        'id': 'number-recognition-20',
                        'title': 'Number Recognition to 20 (Mixed)',
                        'difficulty': 'easy',
                        'explanation': "Spot the numbers hiding in the picture!",
                        'activity': "Click on the numbers 11, 16, and 20.",
                        'example': "Student taps the correct numerals.",
                        'practice': "Click on the numbers 11, 16, and 20.",
                        'visual_aid': "A busy image with numbers 1-20 scattered within it.",
                        'interactive_elements': ['number_hunt', 'hidden_numbers', 'multiple_selection']
                    },
                    {
                        'id': 'place-value-50',
                        'title': 'Place Value (Tens and Ones to 50)',
                        'difficulty': 'medium',
                        'explanation': "Let's look at numbers bigger than 20. How many tens and ones are in 34?",
                        'activity': "Fill in the blanks: 34 has ___ tens and ___ ones.",
                        'example': "Student types '3' and '4'.",
                        'practice': "Fill in the blanks: 34 has ___ tens and ___ ones.",
                        'visual_aid': "Image of base ten blocks representing 34 (3 rods, 4 units).",
                        'interactive_elements': ['place_value', 'base_ten_blocks', 'fill_blanks']
                    },
                    {
                        'id': 'writing-numbers',
                        'title': 'Writing Numbers to 20',
                        'difficulty': 'easy',
                        'explanation': "Practice writing your numbers neatly!",
                        'activity': "Trace the number 18, then write it by yourself.",
                        'example': "Student 'writes' 18 (e.g., using a touch screen or by typing).",
                        'practice': "Trace the number 18, then write it by yourself.",
                        'visual_aid': "Dotted outline of the number 18 for tracing, then a blank space.",
                        'interactive_elements': ['number_tracing', 'writing_practice', 'touch_input']
                    },
                    {
                        'id': 'even-odd',
                        'title': 'Even and Odd Numbers (Introduction)',
                        'difficulty': 'easy',
                        'explanation': "Even numbers can always be shared equally into two groups. Odd numbers always have one left over.",
                        'activity': "Is the number 6 even or odd?",
                        'example': "Student taps 'Even'.",
                        'practice': "Is the number 6 even or odd?",
                        'visual_aid': "Pairs of socks to illustrate even numbers (e.g., 6 socks as 3 pairs).",
                        'interactive_elements': ['even_odd_sorting', 'sock_pairs', 'classification']
                    },
                    {
                        'id': 'number-sequence',
                        'title': 'Finding Missing Numbers in a Sequence (to 20)',
                        'difficulty': 'easy',
                        'explanation': "Help the number train get all its carriages!",
                        'activity': "What number is missing from the train: 10, 11, ___, 13, 14?",
                        'example': "Student types '12'.",
                        'practice': "What number is missing from the train: 10, 11, ___, 13, 14?",
                        'visual_aid': "Image of a train with carriages showing numbers and one blank.",
                        'interactive_elements': ['train_visual', 'sequence_completion', 'missing_number']
                    },
                    {
                        'id': 'counting-from-15',
                        'title': 'Counting up to 20 from any Number',
                        'difficulty': 'easy',
                        'explanation': "Start counting from 15. What are the next 3 numbers?",
                        'activity': "Type the next three numbers in the sequence.",
                        'example': "Student types '16, 17, 18'.",
                        'practice': "Type the next three numbers in the sequence.",
                        'visual_aid': "The number '15' displayed prominently.",
                        'interactive_elements': ['sequence_building', 'multiple_input', 'counting_on']
                    },
                    {
                        'id': 'greater-less-than',
                        'title': 'Comparing Numbers (Greater Than/Less Than to 20)',
                        'difficulty': 'easy',
                        'explanation': "Use the hungry crocodile to pick the bigger number! The crocodile always eats the bigger number.",
                        'activity': "Which number is greater: 12 or 17? Choose the correct crocodile sign (> or <).",
                        'example': "Student taps '<' (should tap '<' because 12 < 17).",
                        'practice': "Which number is greater: 12 or 17? Choose the correct crocodile sign (> or <).",
                        'visual_aid': "Two numbers (12 and 17) with the crocodile signs between them.",
                        'interactive_elements': ['crocodile_comparison', 'symbol_selection', 'number_comparison']
                    },
                    {
                        'id': 'ordering-to-20',
                        'title': 'Ordering Numbers (Smallest to Largest to 20)',
                        'difficulty': 'easy',
                        'explanation': "Put these numbers in order from the smallest to the biggest.",
                        'activity': "Drag the numbers 15, 8, 19, 11 into the correct order.",
                        'example': "Student drags cards to form '8, 11, 15, 19'.",
                        'practice': "Drag the numbers 15, 8, 19, 11 into the correct order.",
                        'visual_aid': "Four number cards: 15, 8, 19, 11.",
                        'interactive_elements': ['drag_drop', 'ordering_sequence', 'number_cards']
                    },
                    {
                        'id': 'number-bonds-20',
                        'title': 'Number Bonds to 20 (Introduction)',
                        'difficulty': 'medium',
                        'explanation': "Can you find two numbers that add up to 20?",
                        'activity': "If you have 15, how many more do you need to make 20?",
                        'example': "Student types '5'.",
                        'practice': "If you have 15, how many more do you need to make 20?",
                        'visual_aid': "20 frame with 15 dots filled.",
                        'interactive_elements': ['twenty_frame', 'number_bonds', 'addition_to_20']
                    },
                    {
                        'id': 'number-words-20',
                        'title': 'Reading and Writing Number Words to 20',
                        'difficulty': 'easy',
                        'explanation': "Practice reading and writing the words for numbers.",
                        'activity': "Read the word 'sixteen' and then type the number.",
                        'example': "Student types '16'.",
                        'practice': "Read the word 'sixteen' and then type the number.",
                        'visual_aid': "The word 'sixteen' written clearly.",
                        'interactive_elements': ['word_recognition', 'number_input', 'reading_practice']
                    },
                    {
                        'id': 'arrays-basic',
                        'title': 'Counting Objects in Arrays (Basic)',
                        'difficulty': 'easy',
                        'explanation': "Sometimes objects are in neat rows. We can count them by rows or columns!",
                        'activity': "How many cookies are there? (Image: 3 rows of 2 cookies)",
                        'example': "Student types '6'.",
                        'practice': "How many cookies are there? (Image: 3 rows of 2 cookies)",
                        'visual_aid': "Image of 3 rows of 2 cookies.",
                        'interactive_elements': ['array_counting', 'row_column_visual', 'cookie_grid']
                    }
                        'visual_aid': "Flashcards showing numerals 1-20.",
                        'interactive_elements': ['number_matching_game', 'flashcard_system', 'drag_drop_numbers']
                    },
                    {
                        'id': 'skip-counting',
                        'title': 'Counting in 1s, 2s, 5s, and 10s',
                        'difficulty': 'easy',
                        'explanation': "Counting can be super speedy! We can count in steps, like counting by 2s or 10s.",
                        'activity': "Skip Count Hop: Hop on a number line, counting in 2s (2, 4, 6...).",
                        'example': "Counting in 5s: 5, 10, 15, 20.",
                        'practice': "What comes next when counting in 10s? 10, 20, 30, ?",
                        'visual_aid': "Animated characters skipping on a number line.",
                        'interactive_elements': ['number_line_hopping', 'skip_count_patterns', 'animated_counting']
                    },
                    {
                        'id': 'before-after-between',
                        'title': 'Before, After, and Between (Numbers to 20)',
                        'difficulty': 'easy',
                        'explanation': "Numbers have neighbours! Some numbers come before, some come after, and some are in between.",
                        'activity': "Missing Number Bridge: Fill in the number that comes before, after, or between.",
                        'example': "What comes after 8? (Answer: 9)",
                        'practice': "What number is between 12 and 14?",
                        'visual_aid': "Three houses with numbers, showing which one is 'before,' 'after,' or 'in between.'",
                        'interactive_elements': ['number_bridge_game', 'house_number_visual', 'sequence_builder']
                    },
                    {
                        'id': 'place-value-20',
                        'title': 'Place Value (Tens and Ones to 20)',
                        'difficulty': 'medium',
                        'explanation': "Big numbers are made of smaller groups! 'Place value' tells us how many groups of 10 and how many single ones a number has.",
                        'activity': "Build a Number: Drag 'ten' sticks and 'one' blocks to make a number (e.g., for 14, drag one 'ten' stick and four 'one' blocks).",
                        'example': "The number 17 is 1 ten and 7 ones. (Image: 1 bundle of 10 sticks and 7 loose sticks)",
                        'practice': "How many tens and ones are in 13?",
                        'visual_aid': "Image of a tens frame filled with 10 dots, and loose dots for ones.",
                        'interactive_elements': ['tens_ones_builder', 'place_value_manipulatives', 'number_construction']
                    }
                ]
            },
            'adding-subtracting-to-10': {
                'lessons': [
                    {
                        'id': 'adding-with-objects',
                        'title': 'Adding with Objects (to 10)',
                        'difficulty': 'easy',
                        'explanation': "Adding means putting groups together to find the total! Let's use our toys to help us.",
                        'activity': "Toy Collector: Drag 3 red cars and 2 blue cars into a box. How many now?",
                        'example': "4 stars + 3 stars = 7 stars.",
                        'practice': "You have 5 apples. Your friend gives you 3 more. How many do you have now?",
                        'visual_aid': "Simple cartoon drawing of objects being combined.",
                        'interactive_elements': ['drag_drop_addition', 'object_combining', 'toy_collector_game']
                    },
                    {
                        'id': 'subtracting-taking-away',
                        'title': 'Subtracting by Taking Away (to 10)',
                        'difficulty': 'easy',
                        'explanation': "Subtracting means taking some away! How many are left?",
                        'activity': "Cookie Muncher: Start with 7 cookies. Click to 'eat' 3. How many are left?",
                        'example': "8 birds - 2 birds = 6 birds.",
                        'practice': "There are 9 flowers. You pick 4. How many are left?",
                        'visual_aid': "Animated scene of objects disappearing from a group.",
                        'interactive_elements': ['cookie_muncher_game', 'disappearing_objects', 'subtraction_animation']
                    },
                    {
                        'id': 'number-bonds-10',
                        'title': 'Number Bonds to 10',
                        'difficulty': 'easy',
                        'explanation': "Number bonds are pairs of numbers that add up to a special total, like 10! Knowing these helps us add fast.",
                        'activity': "Number Bond Pairs: Match the numbers that make 10 (e.g., 3 to 7).",
                        'example': "7 + 3 = 10.",
                        'practice': "What number goes with 4 to make 10?",
                        'visual_aid': "Ten frames with dots filling up.",
                        'interactive_elements': ['number_bond_matching', 'ten_frame_builder', 'bond_pair_game']
                    },
                    {
                        'id': 'addition-number-line',
                        'title': 'Addition on a Number Line',
                        'difficulty': 'easy',
                        'explanation': "A number line helps us jump to find the answer! To add, we jump forwards.",
                        'activity': "Froggy Jumps: Drag a frog on a number line to show 5 + 3.",
                        'example': "To do 6 + 2, start at 6 and jump 2 times forwards. You land on 8.",
                        'practice': "Use the number line to find 7 + 3. (Image: Number line 0-10)",
                        'visual_aid': "Animated jumps on a number line.",
                        'interactive_elements': ['frog_jumping_game', 'animated_number_line', 'forward_jumps']
                    },
                    {
                        'id': 'subtraction-number-line',
                        'title': 'Subtraction on a Number Line',
                        'difficulty': 'easy',
                        'explanation': "To subtract on a number line, we jump backwards! How many jumps back did we make?",
                        'activity': "Rabbit Hops Back: Drag a rabbit on a number line to show 9 - 4.",
                        'example': "To do 10 - 3, start at 10 and jump 3 times backwards. You land on 7.",
                        'practice': "Use the number line to find 8 - 5. (Image: Number line 0-10)",
                        'visual_aid': "Animated backward jumps on a number line.",
                        'interactive_elements': ['rabbit_hopping_game', 'backward_jumps', 'subtraction_line']
                    }
                ]
            },
            'shapes-patterns': {
                'lessons': [
                    {
                        'id': 'recognising-2d-shapes',
                        'title': 'Recognising 2D Shapes',
                        'difficulty': 'easy',
                        'explanation': "Shapes are all around us! 2D shapes are flat, like a picture. Let's find circles, squares, triangles, and rectangles!",
                        'activity': "Shape Sorter: Drag shapes into the correct bin (e.g., 'Square Bin').",
                        'example': "A door is often a rectangle. (Image: Door)",
                        'practice': "Which shape has three sides? (Image: A triangle, a circle, a square)",
                        'visual_aid': "Colourful cartoon representations of 2D shapes.",
                        'interactive_elements': ['shape_sorting_game', 'drag_drop_shapes', 'shape_identification']
                    },
                    {
                        'id': 'recognising-3d-shapes',
                        'title': 'Recognising 3D Shapes',
                        'difficulty': 'easy',
                        'explanation': "3D shapes are 'fat' shapes, not flat! You can hold them. Like a ball is a sphere, and a box is a cube.",
                        'activity': "Spin and Name: Spin a 3D shape and guess its name.",
                        'example': "A dice is a cube. (Image: Dice)",
                        'practice': "What 3D shape is a can of soup?",
                        'visual_aid': "Rotatable 3D models of cubes, spheres, cylinders, cones.",
                        'interactive_elements': ['3d_shape_spinner', 'rotatable_models', 'shape_guessing_game']
                    },
                    {
                        'id': 'making-simple-patterns',
                        'title': 'Making Simple Patterns',
                        'difficulty': 'easy',
                        'explanation': "Patterns are things that repeat! Like red, blue, red, blue. Can you spot the rule?",
                        'activity': "Pattern Builder: Drag and drop coloured blocks to complete an ABAB or ABCABC pattern.",
                        'example': "Circle, Square, Circle, Square, Circle, ____ (Answer: Square)",
                        'practice': "What comes next in this pattern? Apple, Banana, Apple, Banana, Apple, ____",
                        'visual_aid': "Animated repeating patterns.",
                        'interactive_elements': ['pattern_builder', 'color_block_patterns', 'sequence_completion']
                    },
                    {
                        'id': 'shape-properties-2d',
                        'title': 'Identifying Properties of 2D Shapes',
                        'difficulty': 'medium',
                        'explanation': "Shapes have special parts! 'Sides' are the straight lines, and 'vertices' (corners) are the pointy bits where sides meet.",
                        'activity': "Shape Explorer: Click on a shape, and it highlights its sides and vertices.",
                        'example': "A triangle has 3 sides and 3 vertices.",
                        'practice': "How many sides does a square have?",
                        'visual_aid': "Animated highlights of sides and vertices on different 2D shapes.",
                        'interactive_elements': ['shape_explorer', 'interactive_highlighting', 'properties_counter']
                    }
                ]
            },
            'time-oclock-half-past': {
                'lessons': [
                    {
                        'id': 'telling-time-hour',
                        'title': 'Telling Time to the Hour (O\'clock)',
                        'difficulty': 'medium',
                        'explanation': "Clocks help us know when things happen! When the big hand points to 12, it's 'o'clock'.",
                        'activity': "Set the Clock: Drag the clock hands to show 4 o'clock.",
                        'example': "This clock shows 2 o'clock. (Image: Clock showing 2:00)",
                        'practice': "What time is it? (Image: Clock showing 7:00)",
                        'visual_aid': "Analog clock faces with clear hour and minute hands.",
                        'interactive_elements': ['clock_hand_dragging', 'time_setting_game', 'analog_clock_builder']
                    },
                    {
                        'id': 'telling-time-half-past',
                        'title': 'Telling Time to Half Past',
                        'difficulty': 'medium',
                        'explanation': "When the big hand points to the 6, it means 'half past' the hour.",
                        'activity': "Time Match: Match the analog clock to the digital time (e.g., 3:30).",
                        'example': "This clock shows half past 1. (Image: Clock showing 1:30)",
                        'practice': "Draw the hands to show half past 5.",
                        'visual_aid': "Analog clocks demonstrating half-hour positions.",
                        'interactive_elements': ['analog_digital_matching', 'half_past_builder', 'time_conversion']
                    }
                ]
            },
            'money-change': {
                'lessons': [
                    {
                        'id': 'recognizing-uk-coins',
                        'title': 'Recognizing UK Coins',
                        'difficulty': 'medium',
                        'explanation': "Money helps us buy things! Let's learn to spot all the different UK coins and what they are worth.",
                        'activity': "Coin Sorter: Drag coins into bins labelled 1p, 2p, 5p, etc.",
                        'example': "This is a 10p coin. (Image: 10p coin)",
                        'practice': "Which coin is worth the most? (Image: 5p, 10p, 2p coins)",
                        'visual_aid': "Clear, high-resolution images of UK coins (front and back).",
                        'interactive_elements': ['coin_sorting_game', 'value_comparison', 'coin_identification']
                    },
                    {
                        'id': 'counting-small-money',
                        'title': 'Counting Small Amounts of Money',
                        'difficulty': 'medium',
                        'explanation': "Let's count how much money we have! We can add the value of the coins together.",
                        'activity': "Coin Calculator: Drag coins into a box, and the total value appears.",
                        'example': "A 5p coin and a 2p coin is 7p. (Image: 5p and 2p coins)",
                        'practice': "How much money is this? (Image: 10p, 5p, 1p coins)",
                        'visual_aid': "Groups of coins with their total value shown.",
                        'interactive_elements': ['coin_calculator', 'money_totaling', 'drag_drop_coins']
                    }
                ]
            }
        }
    }
    
    return lesson_library.get(subject, {}).get(topic_id, {})

def generate_interactive_lesson_content(subject, topic, lesson_style='visual'):
    """
    Generate comprehensive lesson content based on subject, topic, and learning style
    Returns structured lesson data with activities, examples, and practice questions
    """
    
    # Get the topic data from curriculum
    topic_data = get_lesson_content(subject, topic)
    
    if not topic_data.get('lessons'):
        return generate_fallback_lesson_content(subject, topic, lesson_style)
    
    # Select appropriate lessons based on learning style
    selected_lessons = topic_data['lessons'][:3]  # First 3 lessons for the topic
    
    lesson_content = {
        'title': f'Learning {subject.title()}: {topic.replace("-", " ").title()}',
        'subject': subject,
        'topic': topic,
        'style': lesson_style,
        'lessons': []
    }
    
    for lesson in selected_lessons:
        formatted_lesson = {
            'lesson_title': lesson['title'],
            'difficulty': lesson['difficulty'],
            'explanation': lesson['explanation'],
            'activity': lesson['activity'],
            'example': lesson['example'],
            'practice_question': lesson['practice'],
            'visual_aid': lesson['visual_aid'],
            'interactive_elements': lesson['interactive_elements']
        }
        
        # Customize content based on learning style
        if lesson_style == 'visual':
            formatted_lesson['content'] = generate_visual_content(lesson)
        elif lesson_style == 'auditory':
            formatted_lesson['content'] = generate_auditory_content(lesson)
        else:
            formatted_lesson['content'] = generate_general_content(lesson)
            
        lesson_content['lessons'].append(formatted_lesson)
    
    return lesson_content

def generate_visual_content(lesson):
    """Generate visual-focused content for visual learners"""
    return f"""
    <div class="visual-lesson-content">
        <h3>{lesson['title']}</h3>
        <div class="lesson-explanation">
            <p>{lesson['explanation']}</p>
        </div>
        
        <div class="visual-example">
            <h4>Visual Example:</h4>
            <p>{lesson['example']}</p>
            <div class="visual-aid-suggestion">
                <strong>Visual Aid:</strong> {lesson['visual_aid']}
            </div>
        </div>
        
        <div class="interactive-activity">
            <h4>Try This Activity:</h4>
            <p>{lesson['activity']}</p>
        </div>
        
        <div class="practice-section">
            <h4>Practice Time:</h4>
            <p>{lesson['practice']}</p>
        </div>
    </div>
    """

def generate_auditory_content(lesson):
    """Generate auditory-focused content for auditory learners"""
    return f"""
    <div class="auditory-lesson-content">
        <h3>{lesson['title']}</h3>
        <div class="lesson-explanation">
            <p>🔊 Listen carefully: {lesson['explanation']}</p>
        </div>
        
        <div class="auditory-example">
            <h4>Say It Out Loud:</h4>
            <p>{lesson['example']}</p>
        </div>
        
        <div class="interactive-activity">
            <h4>Speaking Activity:</h4>
            <p>{lesson['activity']}</p>
        </div>
        
        <div class="practice-section">
            <h4>Talk Through This:</h4>
            <p>{lesson['practice']}</p>
        </div>
    </div>
    """

def generate_general_content(lesson):
    """Generate general content for mixed learning styles"""
    return f"""
    <div class="general-lesson-content">
        <h3>{lesson['title']}</h3>
        <div class="lesson-explanation">
            <p>{lesson['explanation']}</p>
        </div>
        
        <div class="example-section">
            <h4>Example:</h4>
            <p>{lesson['example']}</p>
        </div>
        
        <div class="interactive-activity">
            <h4>Interactive Activity:</h4>
            <p>{lesson['activity']}</p>
        </div>
        
        <div class="practice-section">
            <h4>Practice Question:</h4>
            <p>{lesson['practice']}</p>
        </div>
    </div>
    """

def generate_fallback_lesson_content(subject, topic, lesson_style):
    """Generate fallback content when specific lessons aren't available"""
    return {
        'title': f'Learning {subject.title()}: {topic.replace("-", " ").title()}',
        'subject': subject,
        'topic': topic,
        'style': lesson_style,
        'content': f"""
        <div class="lesson-content">
            <h3>Welcome to {subject.title()} Learning!</h3>
            <p>We're preparing amazing lessons for {topic.replace("-", " ")}. 
            This topic will help you learn step by step with fun activities and clear examples.</p>
            
            <div class="coming-soon">
                <h4>What You'll Learn:</h4>
                <ul>
                    <li>Clear explanations with simple language</li>
                    <li>Interactive activities and games</li>
                    <li>Real examples you can understand</li>
                    <li>Practice questions to test your knowledge</li>
                    <li>Visual aids to help you learn</li>
                </ul>
            </div>
        </div>
        """
    }