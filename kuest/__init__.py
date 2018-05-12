import sys
import math
import pygame
from pygame.locals import *
import OpenGL
from OpenGL.GL import *
from pkg_resources import resource_string
import glm

FPS = 35
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT

def die(text):
    """
    Print a string of text to stderr, and then fail.
    
    :param text: the text
    """
    print(text, file=sys.stderr)
    sys.exit(1)

def load_shader(path, kind):
    """
    Load a shader of a given kind from a file.
    
    :param path: the path to the shader source file
    :param kind: the kind of shader, e.g. (GL_FRAGMENT_SHADER, etc.)
    :returns: the handle to the compiled shader
    """
    source = resource_string('kuest', path)
    shader = glCreateShader(kind)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if glGetShaderiv(shader, GL_COMPILE_STATUS) == GL_FALSE:
        die('error: could not compile shader: ' + path)
    return shader

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, OPENGL | DOUBLEBUF)
    
    # Grab the mouse so we can use it for rotation.
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # Only run if the computer supports OpenGL 2.1.
    if not glInitGl21VERSION():
        die('error: OpenGL 2.1 support is required')

    # Set up OpenGL.
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    vert_shader = \
      load_shader('shaders/vertex.v.glsl', GL_VERTEX_SHADER)
    frag_shader = \
      load_shader('shaders/fragment.f.glsl', GL_FRAGMENT_SHADER)
    glsl_program = glCreateProgram()
    glAttachShader(glsl_program, vert_shader)
    glAttachShader(glsl_program, frag_shader)
    glLinkProgram(glsl_program)
    if glGetProgramiv(glsl_program, GL_LINK_STATUS) == GL_FALSE:
        die('error: could not link GLSL program')
    attr_coord3d = glGetAttribLocation(glsl_program, 'coord3d')
    if attr_coord3d == -1:
        die('error: could not bind attribute "coord3d"')
    unif_transform = glGetUniformLocation(glsl_program, 'transform')
    if unif_transform == -1:
        die('error: could not bind uniform "transform"')

    # Set up game state.
    player = {'x': 0.0, 'y': 0.0, 'z': 5.0, 'ydeg': 0.0, 'speed': 0.1}
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEMOTION:
                xoff, yoff = pygame.mouse.get_rel()
                player['ydeg'] += xoff * 0.5
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                    
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[K_w]:
            player['z'] -= math.cos(math.radians(player['ydeg'])) * player['speed']
            player['x'] += math.sin(math.radians(player['ydeg'])) * player['speed']
        elif keys_pressed[K_s]:
            player['z'] += math.cos(math.radians(player['ydeg'])) * player['speed']
            player['x'] -= math.sin(math.radians(player['ydeg'])) * player['speed']
        if keys_pressed[K_d]:
            player['z'] += math.sin(math.radians(player['ydeg'])) * player['speed']
            player['x'] += math.cos(math.radians(player['ydeg'])) * player['speed']
        elif keys_pressed[K_a]:
            player['z'] -= math.sin(math.radians(player['ydeg'])) * player['speed']
            player['x'] -= math.cos(math.radians(player['ydeg'])) * player['speed']
                
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        ## Draw screen contents.
        model = glm.translate(glm.mat4(1.0), glm.tvec3(0.0, 0.0, 0.0))
        
        # Calculate the player's view transformation.
        translation = glm.translate(glm.mat4(1.0),
                                    glm.tvec3(-player['x'],
                                              -player['y'],
                                              -player['z']))
        rotation = glm.rotate(glm.mat4(1.0),
                              glm.radians(player['ydeg']),
                              glm.tvec3(0.0, 1.0, 0.0))
        view = rotation * translation
        
        # Calculate the perspective projection.
        projection = glm.perspective(
                       glm.radians(45.0),
                       float(SCREEN_WIDTH) / float(SCREEN_HEIGHT),
                       0.1, 10.0)
                       
        # Produce the final transformation matrix.
        transform = projection * view * model

        glUseProgram(glsl_program)
        glEnableVertexAttribArray(attr_coord3d)
        vertices = [
            -0.5, 0.5, 0.0,
            -0.5, -0.5, 0.0,
            0.5, -0.5, 0.0,
            0.5, 0.5, 0.0
        ]
        glVertexAttribPointer(attr_coord3d, 3, GL_FLOAT, GL_FALSE, 0, vertices)
        glUniformMatrix4fv(unif_transform, 1, GL_FALSE, glm.value_ptr(transform))
        glDrawArrays(GL_QUADS, 0, 4)
        glDisableVertexAttribArray(attr_coord3d)
        
        pygame.display.flip()
        clock.tick(FPS)
