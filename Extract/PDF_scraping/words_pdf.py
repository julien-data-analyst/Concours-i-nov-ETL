###################################-
# Sujet : Fonction pour rechercher les données à partir d'un mot donné
# Date : 11/12/2025 
###################################-

# Chargement des librairies
import pymupdf

def search_words_extract(searched_word, 
                         search_page,
                         x0_dec_result=0, x1_dec_result=0, 
                         y0_dec_result=0, y1_dec_result=0, 
                         result_elt = 0):
    """
    Function : research the word and send the string result which given by the "dec_result" coordinates.

    Args :
        - searched_word : a string researched word

        - search_page : a object type of "Page" to search the word for

        - x0_dec_result : a float number to shift at x0, 
                            if string "x1" then take the coordinates of the rect.x1 (default : 0)

        - x1_dec_result : a float number to shift at x1, 
                            if string "x0" then take the coordinates of the rect.x0 (default : 0)

        - y0_dec_result : a float number to shift at y0, 
                            if string "y1" then take the coordinates of the rect.y1 (default : 0)

        - y1_dec_result : a float number to shift at y1, 
                            if string "y0" then take the coordinates of the rect.y0 (default : 0)

        - result_elt : which element to take from the result (default : 0)

    Return :
        - result : a string result of the searching
    """

    # Get the occurence list
    occurence_search_word = search_page.search_for(searched_word)

    # If he doesn't find [], then return None
    if occurence_search_word == []:
        #print("Le mot '"+searched_word+"' n'a pas été trouvé")
        result = None
    else:
        # If he does find, take the first element by default
        rect_search_word = occurence_search_word[result_elt]

        # create the result zone
        if x0_dec_result == "x1":
            x0_res = rect_search_word.x1
        else:
            x0_res = rect_search_word.x0 + x0_dec_result

        if x1_dec_result == "x0":
            x1_res = rect_search_word.x0
        else:
            x1_res = rect_search_word.x1 + x1_dec_result

        if y0_dec_result == "y1":
            y0_res = rect_search_word.y1
        else:
            y0_res = rect_search_word.y0 + y0_dec_result

        if y1_dec_result == "y0":
            y1_res = rect_search_word.y0
        else:
            y1_res = rect_search_word.y1 + y1_dec_result

        zone_res = pymupdf.Rect(x0_res, y0_res, x1_res, y1_res)

        # Take the string result
        result = search_page.get_textbox(zone_res).strip()

    return result