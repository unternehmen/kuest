import sys
import math
import pygame
from pygame.locals import *
import OpenGL
from OpenGL.GL import *
from pkg_resources import resource_string
import glm
from ctypes import c_float, c_uint

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
    unif_mvp = glGetUniformLocation(glsl_program, 'mvp')
    if unif_mvp == -1:
        die('error: could not bind uniform "mvp"')
        
    # Models
    cube = {
      'vertices': [
        -0.5, -0.5, -0.5,
        -0.5, -0.5, 0.5,
        -0.5, 0.5, 0.5,
        -0.5, 0.5, -0.5,
        0.5, -0.5, -0.5,
        0.5, -0.5, 0.5,
        0.5, 0.5, 0.5,
        0.5, 0.5, -0.5,
      ],
      'faces': [
        # left
        0, 3, 1,
        3, 2, 1,
        # front
        0, 4, 3,
        4, 7, 3,
        # right
        4, 5, 7,
        5, 6, 7,
        # back
        1, 2, 5,
        2, 6, 5
      ]
    }
    
    verts_buffer = (c_float * len(cube['vertices']))(*cube['vertices'])
    faces_buffer = (c_uint * len(cube['faces']))(*cube['faces'])
    
    vbo_cube_verts = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_cube_verts)
    glBufferData(GL_ARRAY_BUFFER, verts_buffer, GL_STATIC_DRAW)
    
    ibo_cube_elems = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo_cube_elems)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, faces_buffer, GL_STATIC_DRAW)
    
    del verts_buffer
    del faces_buffer

    # Calculate the perspective projection matrix.
    projection = glm.perspective(
                   glm.radians(45.0),
                   float(SCREEN_WIDTH) / float(SCREEN_HEIGHT),
                   0.1, 10.0)

    # Set up game state.
    player = {'x': 2.0, 'y': 0.0, 'z': 2.0, 'ydeg': 0.0, 'tiltdeg': 0.0, 'speed': 0.03}
    stage = {
        'data': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 0, 0, 1, 0, 1, 1, 1, 1, 1,
                 1, 0, 0, 1, 0, 1, 1, 1, 1, 1,
                 1, 1, 0, 0, 0, 1, 1, 1, 1, 1,
                 1, 1, 0, 0, 0, 1, 1, 1, 1, 1,
                 1, 1, 1, 0, 0, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        'width': 10,
        'height': 10
    }
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEMOTION:
                xoff, yoff = pygame.mouse.get_rel()
                player['ydeg'] += xoff * 0.5
                player['tiltdeg'] += yoff * 0.25
                if player['tiltdeg'] < -90.0:
                    player['tiltdeg'] = -90.0
                elif player['tiltdeg'] > 90.0:
                    player['tiltdeg'] = 90.0
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit()
                    
        keys_pressed = pygame.key.get_pressed()
        xcomp = math.cos(math.radians(player['ydeg']))
        zcomp = math.sin(math.radians(player['ydeg']))
        if keys_pressed[K_w]:
            player['z'] -= xcomp * player['speed']
            player['x'] += zcomp * player['speed']
        elif keys_pressed[K_s]:
            player['z'] += xcomp * player['speed']
            player['x'] -= zcomp * player['speed']
        if keys_pressed[K_d]:
            player['z'] += zcomp * player['speed']
            player['x'] += xcomp * player['speed']
        elif keys_pressed[K_a]:
            player['z'] -= zcomp * player['speed']
            player['x'] -= xcomp * player['speed']
                
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        ## Draw screen contents.
        
        # Calculate the player's view transformation.
        translation = glm.translate(glm.mat4(1.0),
                                    glm.tvec3(-player['x'],
                                              -player['y'],
                                              -player['z']))
        rotation = glm.rotate(glm.mat4(1.0),
                              glm.radians(player['ydeg']),
                              glm.tvec3(0.0, 1.0, 0.0))
        tilt = glm.rotate(glm.mat4(1.0),
                          glm.radians(player['tiltdeg']),
                          glm.tvec3(1.0, 0.0, 0.0))
        view = tilt * rotation * translation
                       
        # Produce the final world matrix.
        transform = projection * view

        glUseProgram(glsl_program)
        glEnableVertexAttribArray(attr_coord3d)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_cube_verts)
        glVertexAttribPointer(attr_coord3d, 3, GL_FLOAT, GL_FALSE, 0, None)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo_cube_elems)
        for y in range(stage['height']):
            for x in range(stage['width']):
                i = y * stage['width'] + x
                if stage['data'][i] == 1:
                    model = glm.translate(glm.mat4(1.0),
                                          glm.tvec3(float(x),
                                                    0.0,
                                                    float(y)))
                    mvp = transform * model
                    glUniformMatrix4fv(unif_mvp, 1, GL_FALSE,
                                       glm.value_ptr(mvp))
                    glDrawElements(GL_TRIANGLES,
                                   len(cube['faces']),
                                   GL_UNSIGNED_INT, None)
        
        glDisableVertexAttribArray(attr_coord3d)
        
        pygame.display.flip()
        clock.tick(FPS)
