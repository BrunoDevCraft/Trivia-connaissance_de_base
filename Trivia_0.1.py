import os
import pygame
import sys
import traceback
import random
from pathlib import Path

pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trivia Game")

# Utilisez Path pour obtenir le chemin absolu du dossier contenant le script
script_path = Path(__file__).resolve().parent

assets_path = Path(getattr(sys, '_MEIPASS', script_path)) / "assets"
themes_path = assets_path / "themes"

class PresentationScreen:
    def __init__(self, surface):
        self.surface = surface
        self.font_title = pygame.font.Font(None, 48)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_button = pygame.font.Font(None, 36)
        self.start_rect = self.font_button.render("START", True, (255, 255, 255)).get_rect()

    def display(self):
        # Affiche le titre du jeu et le bouton "START"
        title_text_line1 = "JEU DU TRIVIA"
        title_text_line2 = "Connaissance de Base"
        title_surface_line1 = self.font_title.render(title_text_line1, True, (255, 255, 255))
        title_surface_line2 = self.font_title.render(title_text_line2, True, (255, 255, 255))
        title_position_line1 = (WIDTH // 2 - title_surface_line1.get_width() // 2, HEIGHT // 3)
        title_position_line2 = (WIDTH // 2 - title_surface_line2.get_width() // 2, HEIGHT // 3 + title_surface_line1.get_height())
        self.surface.blit(title_surface_line1, title_position_line1)
        self.surface.blit(title_surface_line2, title_position_line2)

        start_text = "START"
        start_surface = self.font_button.render(start_text, True, (255, 255, 255))
        self.start_rect.topleft = (WIDTH // 2 - start_surface.get_width() // 2, 2 * HEIGHT // 3)
        self.surface.blit(start_surface, self.start_rect.topleft)

    def handle_event(self, event):
        # Vérifie si le bouton "START" est cliqué
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.start_rect.collidepoint(mouse_x, mouse_y):
                return True
        return False

class ThemeSelectionScreen:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(None, 36)
        self.themes = ["numerique", "histoire", "geographie", "musique"]
        self.selected_theme = None

    def display(self):
        # Affiche le titre de la sélection de thème et les thèmes disponibles
        title_text = "Sélectionnez un thème"
        title_surface = self.font.render(title_text, True, (255, 255, 255))
        x_position = (WIDTH - title_surface.get_width()) // 2
        y_position = HEIGHT // 3
        self.surface.blit(title_surface, (x_position, y_position))

        for i, theme in enumerate(self.themes):
            theme_text = f"{i + 1}. {theme}"
            theme_surface = self.font.render(theme_text, True, (255, 255, 255))
            x_position = (WIDTH - theme_surface.get_width()) // 2
            y_position = HEIGHT // 3 + (i + 1) * self.font.get_height() * 1.5
            self.surface.blit(theme_surface, (x_position, y_position))

    def handle_event(self, event):
        # Vérifie si l'un des thèmes est sélectionné
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for i, theme in enumerate(self.themes):
                theme_rect = pygame.Rect((WIDTH - self.font.size(f"{i + 1}. {theme}")[0]) // 2,
                                         HEIGHT // 3 + (i + 1) * self.font.get_height() * 1.5,
                                         self.font.size(f"{i + 1}. {theme}")[0],
                                         self.font.size(f"{i + 1}. {theme}")[1])
                if theme_rect.collidepoint(mouse_x, mouse_y):
                    self.selected_theme = theme
                    return True
        return False

class TriviaGame:
    
    def __init__(self, surface, selected_theme, nb_questions):
        # Initialisation du jeu avec les paramètres nécessaires
        self.surface = surface
        self.score = 0
        self.current_question = 0
        self.questions = self.load_questions(selected_theme, nb_questions)
        self.font = pygame.font.Font(None, 36)
        self.answer_display_time = None
        self.result_display_time = None
        self.result_text = None
        self.answer_checked = False
        self.already_checked_text = None
        self.game_over = False
        self.lives = 10
        self.y_position_options = 310
        
    def display_question(self):
        # Affiche la question actuelle et les options
        if 0 <= self.current_question < len(self.questions):
            question_text = self.questions[self.current_question]["question"]
            question_lines = self.wrap_text(question_text, self.font, WIDTH - 100)

            # Calcul de la hauteur totale de la question
            total_question_height = sum(self.font.get_height() for line in question_lines)

            # Affichage de la question à la même hauteur
            y_position = (HEIGHT - total_question_height - len(self.questions[self.current_question]["options"]) * self.font.get_height() - 40) // 2
            
            for line in question_lines:
                question_surface = self.font.render(line, True, (255, 255, 255))
                x_position = (WIDTH - question_surface.get_width()) // 2
                self.surface.blit(question_surface, (x_position, y_position))
                y_position += self.font.get_height()

            options = self.questions[self.current_question]["options"]
            max_option_width = max(self.font.size(f"{i + 1}. {option}")[0] for i, option in enumerate(options))
            max_option_height = max(self.font.size(f"{i + 1}. {option}")[1] for i, option in enumerate(options))
            y_position = self.y_position_options 

            for i, option in enumerate(options):
                option_text = f"{i + 1}. {option}"
                option_surface = self.font.render(option_text, True, (255, 255, 255))
                self.surface.blit(option_surface, ((WIDTH - max_option_width) // 2, y_position + i * max_option_height))

            score_text = f"Score: {self.score} / {self.current_question + 1}"
            score_surface = self.font.render(score_text, True, (255, 255, 255))
            self.surface.blit(score_surface, (10, 10))

            lives_text = f"Vies: {self.lives}"
            lives_surface = self.font.render(lives_text, True, (255, 255, 255))
            self.surface.blit(lives_surface, (WIDTH - lives_surface.get_width() - 10, 10))
                 
    def handle_mouse_event(self, event):
        # Gestion des événements de la souris pour les options
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Vérifie si le clic de la souris est sur l'une des options
            options = self.questions[self.current_question]["options"]
            max_option_width = max(self.font.size(f"{i + 1}. {option}")[0] for i, option in enumerate(options))
            max_option_height = max(self.font.size(f"{i + 1}. {option}")[1] for i, option in enumerate(options))
            x_position = (WIDTH - max_option_width) // 2
            y_position = 200 + len(options) * self.font.get_height() + 40 

            # Si le clic est en dehors de la zone des options, retourne None
            if not (x_position <= mouse_x <= x_position + max_option_width and
                    y_position <= mouse_y <= y_position + len(options) * max_option_height):
                return None
            
            for i, option in enumerate(options):
                option_rect = pygame.Rect(x_position, y_position + i * max_option_height, max_option_width, max_option_height)
                if option_rect.collidepoint(mouse_x, mouse_y):
                    return i

        return None
    
    def display_result_text(self, result_text):
        # Affiche le texte du résultat après chaque question
        result_surface = self.font.render(result_text, True, (255, 255, 255))
        x_position = (WIDTH - result_surface.get_width()) // 2
        y_position = 200 + len(self.questions[self.current_question]["options"]) * self.font.get_height() + 40
        self.surface.blit(result_surface, (x_position, y_position))
        self.result_display_time = None

    def wrap_text(self, text, font, max_width):
        # Enveloppe le texte pour qu'il tienne dans la largeur spécifiée
        words = text.split(' ')
        lines = []
        current_line = words[0]

        for word in words[1:]:
            test_line = current_line + ' ' + word
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines

    def load_questions(self, selected_theme, nb_questions):
        # Utilisez le chemin absolu pour accéder au fichier de questions
        questions_file_path = themes_path / f"{selected_theme}.txt"
        
        # Charge les questions depuis un fichier en fonction du thème sélectionné
        try:
            #print("Répertoire de travail actuel:", os.getcwd())
            questions = []
            with open(questions_file_path, "r") as file:
                for line in file:
                    question_data = line.strip().split("|")
                    if len(question_data) == 3:
                        question_text, options_str, correct_answer = question_data
                        options = options_str.split(",")
                        correct_answer = str(correct_answer)
                        questions.append({"question": question_text, "options": options, "correct": correct_answer})

            random.shuffle(questions)
            return questions[:nb_questions]
        except FileNotFoundError as e:
            print(f"Erreur : fichier de questions introuvable ({questions_file_path})")
            traceback.print_exc()
            return []
        except Exception as e:
            print("Erreur lors du chargement des questions :", e)
            traceback.print_exc()
            return []

    def check_answer(self, selected_option):
        # Vérifie la réponse sélectionnée par le joueur
        result_text = None  # Initialisation de result_text en dehors de la condition
        
        if not self.answer_checked:
            if 0 <= self.current_question < len(self.questions):
                correct_answer = self.questions[self.current_question]["correct"]
                if str(selected_option) == correct_answer:
                    result_text = "Correct"
                    self.score += 1
                elif str(selected_option) != correct_answer:
                    result_text = "Incorrect"
                    self.lives -= 1
                else:
                    result_text = "Déjà vérifié"
                
                self.answer_checked = True  # Marquer la réponse comme vérifiée
                    
        self.answer_display_time = pygame.time.get_ticks()
        
        # Vérifie si le jeu est terminé après chaque réponse
        if self.current_question >= len(self.questions) or self.lives <= 0:
            self.game_over = True
            
        return result_text

    def display_result(self):
        # Affiche le résultat de la réponse pendant un certain temps
        if self.answer_display_time is not None:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.answer_display_time

            if elapsed_time < 3000:
                return self.result_text
            else:
                self.answer_checked = False
                self.answer_display_time = None
                self.result_display_time = pygame.time.get_ticks()
                return None 

    def is_result_displayed(self):
        # Vérifie si le résultat est affiché
        if self.result_display_time is not None:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.result_display_time
            return elapsed_time < 3000

class ResultWindow:
    def __init__(self, surface, result_text):
        # Fenêtre de résultat affichée après chaque réponse
        self.surface = surface
        self.result_text = result_text
        self.font = pygame.font.Font(None, 48)
        self.display_time = None

    def display(self):
        # Affiche le résultat pendant un certain temps
        if self.display_time is None:
            self.display_time = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.display_time

        if elapsed_time < 3000:
            result_surface = self.font.render(self.result_text, True, (255, 255, 255))
            self.surface.blit(result_surface, (WIDTH // 2 - result_surface.get_width() // 2, HEIGHT // 1.25 - result_surface.get_height() // 2))

class GameOverScreen:
    GAME_OVER_DISPLAY_DURATION = 5000  # Mettez la durée souhaitée en millisecondes
    def __init__(self, surface):
        # Écran affiché lorsque le joueur n'a plus de vies
        self.surface = surface
        self.font = pygame.font.Font(None, 36)
        self.message_lines = [
            "Ce n'est que partie remise,",
            "pour avancer, il faut souvent tomber;",
            "Mais le plus important c'est de se relever."
        ]
        
    def display(self):
        # Affiche le message de l'écran de fin de partie
        for i, line in enumerate(self.message_lines):
            line_surface = self.font.render(line, True, (255, 255, 255))
            x_position = (WIDTH - line_surface.get_width()) // 2
            y_position = HEIGHT // 3 + i * self.font.get_height()
            self.surface.blit(line_surface, (x_position, y_position))
        # Ajoutez une vérification pour quitter le jeu lorsque le message est affiché
        #self.quit_game = True
        
class EndScreen:
    DISPLAY_DURATION = 5000  # Durée d'affichage de l'écran de fin
    
    def __init__(self, surface, final_score):
        # Initialisation de l'écran de fin avec la surface et le score final
        self.surface = surface
        self.final_score = final_score
        self.font = pygame.font.Font(None, 48)
        self.display_time = None
        self.end_messages = ["Partie terminée", "Stock question épuisée", f"Score final : {self.final_score}"]
        self.current_message_index = 0
    
    def display(self):
        # Affiche l'écran de fin avec le message correspondant
        if self.display_time is None:
            self.display_time = pygame.time.get_ticks()

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.display_time

        if elapsed_time < self.DISPLAY_DURATION:
            end_text = self.end_messages[self.current_message_index]
            end_surface = self.font.render(end_text, True, (255, 255, 255))
            x_position = (WIDTH - end_surface.get_width()) // 2
            y_position = HEIGHT // 2 - end_surface.get_height() // 2
            self.surface.blit(end_surface, (x_position, y_position))
        else:
            self.current_message_index += 1
            if self.current_message_index >= len(self.end_messages):
                self.current_message_index = 0
            self.display_time = current_time
            
def main():
    presentation_screen = PresentationScreen(win)
    theme_selection_screen = ThemeSelectionScreen(win)
    game = None
    result_window = None
    game_over_screen = GameOverScreen(win)
    end_screen = None
    display_result_time = 0
    end_screen_displayed = False
    
    in_presentation_screen = True
    in_theme_selection_screen = False
    running = True
 
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if in_presentation_screen:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if presentation_screen.handle_event(event):
                        in_presentation_screen = False
                        in_theme_selection_screen = True
            elif in_theme_selection_screen:
                theme_selection_screen.display()
                if theme_selection_screen.handle_event(event):
                    in_theme_selection_screen = False
                    game = TriviaGame(win, theme_selection_screen.selected_theme, 30)
            elif game is not None and not end_screen_displayed:
                if game.lives > 0:
                    if event.type == pygame.KEYDOWN:
                        if result_window is None and not game.is_result_displayed():
                            if pygame.K_1 <= event.key <= pygame.K_3:
                                option_index = event.key - pygame.K_1
                                result_text = game.check_answer(option_index)
                                result_window = ResultWindow(win, result_text)
                                game.display_result_text(result_text)

                    # Gestion d'événements pour la souris
                    mouse_option = game.handle_mouse_event(event)
                    if mouse_option is not None:
                        result_text = game.check_answer(mouse_option)
                        result_window = ResultWindow(win, result_text)
                        game.display_result_text(result_text)

                        if result_window is not None:
                            display_result_time = pygame.time.get_ticks()
                else:
                    if result_window is None:
                        result_window = ResultWindow(win, "Game Over")
                    
                    result_window.display()

                    if pygame.time.get_ticks() - display_result_time >= 3000:
                        result_window = None
                        end_screen = EndScreen(win, game.score)
                        end_screen.display()
                        end_screen_displayed = True                
                        
        win.fill((0, 0, 0))

        if in_presentation_screen:
            presentation_screen.display()
        elif in_theme_selection_screen:
            theme_selection_screen.display()
        elif game is not None and not end_screen_displayed:
            if game.lives > 0:
                if game.current_question < len(game.questions):
                    game.display_question()
                else:
                    # Toutes les questions ont été répondues, affichez l'écran de fin
                    if not end_screen_displayed:
                        end_screen = EndScreen(win, game.score)
                        end_screen.display()
                        end_screen_displayed = True
                        display_result_time = pygame.time.get_ticks()
                    
                    # Ajoutez la vérification pour quitter le jeu lorsque l'écran de fin est affiché
                    if pygame.time.get_ticks() - display_result_time >= EndScreen.DISPLAY_DURATION:
                        running = False
            else:
                if game_over_screen is not None:
                    game_over_screen.display()
                    if pygame.time.get_ticks() - display_result_time >= GameOverScreen.GAME_OVER_DISPLAY_DURATION:
                        running = False  
                              
        if result_window is not None:
            result_window.display()
            result_text = game.display_result()
            if result_text is not None:
                result_window.result_text = result_text
                result_window.display()

            if pygame.time.get_ticks() - display_result_time >= 3000:
                result_window = None
                if game.current_question < len(game.questions):
                    game.current_question += 1
        if end_screen is not None and end_screen_displayed:
            # Affichez l'écran de fin sans mettre à jour les autres éléments
            end_screen.display()
            
        pygame.display.flip()
        pygame.time.Clock().tick(30)

if __name__ == "__main__":
    main()
