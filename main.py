import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BORDER_MARGIN = 50
BORDER_RECT = pygame.Rect(BORDER_MARGIN, BORDER_MARGIN, 
                         SCREEN_WIDTH - 2 * BORDER_MARGIN, 
                         SCREEN_HEIGHT - 2 * BORDER_MARGIN)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

class Car:
    def __init__(self, x, y):
        self.initial_x = x
        self.initial_y = y
        self.x = x
        self.y = y
        self.angle = 0  # Car body angle in degrees
        self.front_wheel_angle = 0  # Front wheel steering angle in degrees
        self.speed_levels = [0, 0.5, 1.0, 1.5, 2.0]  # Reduced speed levels for keys 1-4
        self.current_speed_level = 1
        self.steering_speeds = [0.05, 0.6, 1.0, 1.5]  # Steering speeds for 5,6,7,8
        self.auto_rewind_speeds = [0.05, 0.6, 1.0, 1.5]  # Auto rewind speeds - same as steering speeds
        self.current_steering_speed = 1  # Default to 6 (index 1)
        
        # Car dimensions
        self.width = 50
        self.height = 100
        self.wheel_width = 12
        self.wheel_height = 20
        self.wheelbase = 70  # Distance between front and rear axles
        
        # Line plotting
        self.front_wheel_trail = []  # Store front wheel positions
        self.show_trail = False
        
        # Car visibility
        self.car_visible = True
        
    def update_steering(self, direction):
        """Update front wheel steering angle"""
        steering_speed = self.steering_speeds[self.current_steering_speed]
        max_steering_angle = 30  # Maximum steering angle in degrees
        
        self.front_wheel_angle += direction * steering_speed
        # Clamp steering angle
        self.front_wheel_angle = max(-max_steering_angle, 
                                   min(max_steering_angle, self.front_wheel_angle))
    
    def move(self, direction):
        """Move car forward (1) or backward (-1)"""
        speed = self.speed_levels[self.current_speed_level] * direction
        
        if speed == 0:
            return
            
        # Calculate movement based on current car angle
        angle_rad = math.radians(self.angle)
        
        # Calculate new position
        new_x = self.x + speed * math.sin(angle_rad)
        new_y = self.y - speed * math.cos(angle_rad)  # Negative because y increases downward
        
        # Check border collision
        margin = max(self.width, self.height) // 2 + 10
        if (BORDER_RECT.left + margin <= new_x <= BORDER_RECT.right - margin and
            BORDER_RECT.top + margin <= new_y <= BORDER_RECT.bottom - margin):
            
            self.x = new_x
            self.y = new_y
            
            # Add front wheel positions to trail if showing
            if self.show_trail:
                front_wheel_positions = self.get_front_wheel_positions()
                self.front_wheel_trail.extend(front_wheel_positions)
            
            # Update car rotation based on bicycle model physics
            if abs(speed) > 0.1:  # Only rotate if moving
                # Bicycle model: rear wheels follow, front wheels steer
                steering_rad = math.radians(self.front_wheel_angle)
                angular_velocity = (speed / self.wheelbase) * math.tan(steering_rad)
                self.angle += math.degrees(angular_velocity)
                
                # Keep angle in reasonable range
                self.angle = self.angle % 360
    
    def get_front_wheel_positions(self):
        """Get current front wheel positions"""
        front_wheel_y = -self.wheelbase // 2
        wheel_x_left = -self.width // 3
        wheel_x_right = self.width // 3
        
        car_angle_rad = math.radians(self.angle)
        
        # Left front wheel
        left_x = self.x + (wheel_x_left * math.cos(car_angle_rad) - front_wheel_y * math.sin(car_angle_rad))
        left_y = self.y + (wheel_x_left * math.sin(car_angle_rad) + front_wheel_y * math.cos(car_angle_rad))
        
        # Right front wheel
        right_x = self.x + (wheel_x_right * math.cos(car_angle_rad) - front_wheel_y * math.sin(car_angle_rad))
        right_y = self.y + (wheel_x_right * math.sin(car_angle_rad) + front_wheel_y * math.cos(car_angle_rad))
        
        return [(left_x, left_y), (right_x, right_y)]
    
    def set_speed_level(self, level):
        """Set speed level (1-4)"""
        if 1 <= level <= 4:
            self.current_speed_level = level
    
    def set_steering_speed(self, level):
        """Set steering speed (0-3 for 5,6,7,8) - auto rewind speed matches automatically"""
        if 0 <= level < len(self.steering_speeds):
            self.current_steering_speed = level
    
    def get_current_auto_rewind_speed(self):
        """Get current auto rewind speed (same as steering speed)"""
        return self.auto_rewind_speeds[self.current_steering_speed]
    
    def auto_rewind_steering(self):
        """Gradually return steering to center"""
        if abs(self.front_wheel_angle) > 0.1:
            # Use the auto rewind speed which matches steering speed
            rewind_speed = self.get_current_auto_rewind_speed()
            # Reduce the steering angle by the rewind speed
            if self.front_wheel_angle > 0:
                self.front_wheel_angle -= rewind_speed
                if self.front_wheel_angle < 0:
                    self.front_wheel_angle = 0
            else:
                self.front_wheel_angle += rewind_speed
                if self.front_wheel_angle > 0:
                    self.front_wheel_angle = 0
        else:
            self.front_wheel_angle = 0
    
    def reset_position(self):
        """Reset car to initial position and clear trail"""
        self.x = self.initial_x
        self.y = self.initial_y
        self.angle = 0
        self.front_wheel_angle = 0
        self.front_wheel_trail.clear()
    
    def toggle_trail(self):
        """Toggle trail display"""
        self.show_trail = not self.show_trail
    
    def clear_trail(self):
        """Clear existing trail"""
        self.front_wheel_trail.clear()
    
    def toggle_car_visibility(self):
        """Toggle car visibility"""
        self.car_visible = not self.car_visible
    
    def draw_trail(self, screen):
        """Draw the front wheel trail"""
        if not self.show_trail or len(self.front_wheel_trail) < 2:
            return
        
        # Draw trail points
        for i in range(0, len(self.front_wheel_trail) - 1, 2):  # Step by 2 since we have pairs
            if i + 1 < len(self.front_wheel_trail):
                # Draw a small circle for each front wheel position
                pygame.draw.circle(screen, CYAN, (int(self.front_wheel_trail[i][0]), 
                                                int(self.front_wheel_trail[i][1])), 2)
                pygame.draw.circle(screen, MAGENTA, (int(self.front_wheel_trail[i+1][0]), 
                                                   int(self.front_wheel_trail[i+1][1])), 2)
        
        # Connect the points with lines
        if len(self.front_wheel_trail) >= 4:
            # Left wheel trail (cyan)
            left_points = [self.front_wheel_trail[i] for i in range(0, len(self.front_wheel_trail), 2)]
            if len(left_points) >= 2:
                pygame.draw.lines(screen, CYAN, False, left_points, 1)
            
            # Right wheel trail (magenta)
            right_points = [self.front_wheel_trail[i] for i in range(1, len(self.front_wheel_trail), 2)]
            if len(right_points) >= 2:
                pygame.draw.lines(screen, MAGENTA, False, right_points, 1)
    
    def draw(self, screen):
        """Draw the complete car and trail"""
        # Always draw trail first (behind car)
        self.draw_trail(screen)
        
        # Only draw car if visible
        if self.car_visible:
            # Draw car body
            self.draw_car_body(screen)
            
            # Draw wheels
            self.draw_wheels(screen)
    
    def draw_car_body(self, screen):
        """Draw the main car body"""
        # Create car surface
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw main body
        pygame.draw.rect(car_surface, BLUE, (5, 10, self.width-10, self.height-20))
        
        # Draw front and rear bumpers
        pygame.draw.rect(car_surface, GRAY, (8, 0, self.width-16, 15))  # Front bumper
        pygame.draw.rect(car_surface, GRAY, (8, self.height-15, self.width-16, 15))  # Rear bumper
        
        # Draw windshield
        pygame.draw.rect(car_surface, WHITE, (10, 15, self.width-20, 20))
        
        # Rotate and position car
        rotated_car = pygame.transform.rotate(car_surface, -self.angle)
        car_rect = rotated_car.get_rect(center=(self.x, self.y))
        screen.blit(rotated_car, car_rect)
    
    def draw_wheels(self, screen):
        """Draw all four wheels"""
        # Wheel positions relative to car center
        front_wheel_y = -self.wheelbase // 2
        rear_wheel_y = self.wheelbase // 2
        wheel_x_left = -self.width // 3
        wheel_x_right = self.width // 3
        
        # Draw front wheels (steered)
        front_wheel_angle = self.angle + self.front_wheel_angle
        self.draw_wheel(screen, wheel_x_left, front_wheel_y, front_wheel_angle, RED)
        self.draw_wheel(screen, wheel_x_right, front_wheel_y, front_wheel_angle, RED)
        
        # Draw rear wheels (fixed)
        self.draw_wheel(screen, wheel_x_left, rear_wheel_y, self.angle, GREEN)
        self.draw_wheel(screen, wheel_x_right, rear_wheel_y, self.angle, GREEN)
    
    def draw_wheel(self, screen, x_offset, y_offset, wheel_angle, color):
        """Draw a single wheel at the specified offset and angle"""
        # Transform offset to world coordinates
        car_angle_rad = math.radians(self.angle)
        world_x = self.x + (x_offset * math.cos(car_angle_rad) - y_offset * math.sin(car_angle_rad))
        world_y = self.y + (x_offset * math.sin(car_angle_rad) + y_offset * math.cos(car_angle_rad))
        
        # Create wheel surface
        wheel_surface = pygame.Surface((self.wheel_width, self.wheel_height), pygame.SRCALPHA)
        pygame.draw.rect(wheel_surface, color, (0, 0, self.wheel_width, self.wheel_height))
        pygame.draw.rect(wheel_surface, BLACK, (2, 2, self.wheel_width-4, self.wheel_height-4), 2)
        
        # Rotate wheel
        rotated_wheel = pygame.transform.rotate(wheel_surface, -wheel_angle)
        wheel_rect = rotated_wheel.get_rect(center=(world_x, world_y))
        screen.blit(rotated_wheel, wheel_rect)

def draw_border(screen):
    """Draw the movement boundary"""
    pygame.draw.rect(screen, WHITE, BORDER_RECT, 3)
    
    # Draw corner markers
    corner_size = 20
    pygame.draw.rect(screen, YELLOW, (BORDER_RECT.left, BORDER_RECT.top, corner_size, corner_size))
    pygame.draw.rect(screen, YELLOW, (BORDER_RECT.right-corner_size, BORDER_RECT.top, corner_size, corner_size))
    pygame.draw.rect(screen, YELLOW, (BORDER_RECT.left, BORDER_RECT.bottom-corner_size, corner_size, corner_size))
    pygame.draw.rect(screen, YELLOW, (BORDER_RECT.right-corner_size, BORDER_RECT.bottom-corner_size, corner_size, corner_size))

def draw_instructions(screen, car):
    """Draw control instructions and current status"""
    font_title = pygame.font.Font(None, 26)
    font_text = pygame.font.Font(None, 22)
    
    # Title
    title = font_title.render("CAR SIMULATION CONTROLS", True, YELLOW)
    screen.blit(title, (SCREEN_WIDTH - 290, 10))
    
    # Instructions
    instructions = [
        "",
        "MOVEMENT:",
        "D - Move Forward",
        "R - Move Backward",
        "A - Reset Position",
        "",
        "STEERING:",
        "← → - Steer Left/Right",
        "",
        "SPEED LEVELS:",
        "1, 2, 3, 4 - Set Speed",
        "",
        "STEERING SPEED:",
        "5, 6, 7, 8 - Set Rate",
        "(Auto rewind matches)",
        "",
        "TRAIL PLOTTING:",
        "Q - Toggle Trail Display",
        "P - Clear Trail",
        "",
        "CAR VISIBILITY:",
        "T - Toggle Car Visibility",
        "",
        "CURRENT STATUS:",
        f"Speed Level: {car.current_speed_level}",
        f"Steering Speed: {car.current_steering_speed + 1} ({car.steering_speeds[car.current_steering_speed]})",
        f"Auto Rewind: {car.get_current_auto_rewind_speed()}",
        f"Front Wheel Angle: {car.front_wheel_angle:.1f}°",
        f"Car Angle: {car.angle:.1f}°",
        f"Trail Display: {'ON' if car.show_trail else 'OFF'}",
        f"Trail Points: {len(car.front_wheel_trail)}",
        f"Car Visible: {'YES' if car.car_visible else 'NO'}",
        "",
        "WHEELS:",
        "RED - Front (Steered)",
        "GREEN - Rear (Fixed)",
        "",
        # "TRAIL COLORS:",
        # "CYAN - Left Front Wheel",
        # "MAGENTA - Right Front Wheel"
    ]
    
    y = 60
    for instruction in instructions:
        if instruction == "":
            y += 8
            continue
            
        if instruction.startswith(("MOVEMENT:", "STEERING:", "SPEED LEVELS:", "STEERING SPEED:", 
                                 "TRAIL PLOTTING:", "CAR VISIBILITY:",
                                 "CURRENT STATUS:", "WHEELS:", "TRAIL COLORS:")):
            color = WHITE
            font = font_title
        else:
            color = GRAY
            font = font_text
            
        text = font.render(instruction, True, color)
        screen.blit(text, (SCREEN_WIDTH - 280, y))
        y += 22

def main():
    """Main game loop"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Car Simulation Game - Enhanced")
    clock = pygame.time.Clock()
    
    # Create car in center of movement area
    car = Car(BORDER_RECT.centerx, BORDER_RECT.centery)
    
    # Track held keys for smooth movement
    keys_held = set()
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                keys_held.add(event.key)
                
                # Speed level selection
                if event.key == pygame.K_1:
                    car.set_speed_level(1)
                elif event.key == pygame.K_2:
                    car.set_speed_level(2)
                elif event.key == pygame.K_3:
                    car.set_speed_level(3)
                elif event.key == pygame.K_4:
                    car.set_speed_level(4)
                
                # Steering speed selection (5,6,7,8)
                elif event.key == pygame.K_5:
                    car.set_steering_speed(0)
                elif event.key == pygame.K_6:
                    car.set_steering_speed(1)
                elif event.key == pygame.K_7:
                    car.set_steering_speed(2)
                elif event.key == pygame.K_8:
                    car.set_steering_speed(3)
                
                # Reset position
                elif event.key == pygame.K_a:
                    car.reset_position()
                
                # Trail controls
                elif event.key == pygame.K_q:
                    car.toggle_trail()
                elif event.key == pygame.K_p:
                    car.clear_trail()
                
                # Car visibility toggle
                elif event.key == pygame.K_t:
                    car.toggle_car_visibility()
                    
            elif event.type == pygame.KEYUP:
                keys_held.discard(event.key)
        
        # Handle continuous key presses
        if pygame.K_LEFT in keys_held:
            car.update_steering(-1)
        if pygame.K_RIGHT in keys_held:
            car.update_steering(1)
        if pygame.K_d in keys_held:
            car.move(1)  # Forward
        if pygame.K_r in keys_held:
            car.move(-1)  # Backward
        
        # Auto rewind steering when not turning
        if pygame.K_LEFT not in keys_held and pygame.K_RIGHT not in keys_held:
            car.auto_rewind_steering()
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw game elements
        draw_border(screen)
        car.draw(screen)
        draw_instructions(screen, car)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()