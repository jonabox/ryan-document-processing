# Ryan Document Processing Project

### Code File Explanations
* makeTemplate.py is used to create a template for the specific type of document you are trying to analyze. You select boxes around text, checkboxes, and signatures you want to analyze, and the code saves the boxes you selected in a named template. 

* main.py is used to analyze a document using a pre-made template. The code takes as input the name of the template, finds the template from the list of pre-made ones, and uses the template to analyze the document. It prints the text, which checkbox is checked, and if a signature exists into the terminal. 

* checkbox.py contains helper functions that detect and analyze checkboxes. 

### Demo Instructions
* Run makeTemplate.py and enter the region as "AZ" when prompted in your terminal.

* A document will pop up - use your cursor to select a box around the text you want to extract, and press enter. Continue to do this for all of the text boxes, and then press ESC to finish the selection process for text. 

* Repeat for checkboxes and signatures. 

* Run main.py and again enter "AZ" as the region when prompted. The demo will display each crop that you selected (press any key to move on to the next crop), and the text from the crop will be printed into your terminal. 

* After going through all the boxes, a final list of all the texts, checkboxes, and signatures will be printed into the terminal.
