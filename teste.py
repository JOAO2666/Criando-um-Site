import pygame

pygame.init()
tela = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Teste")

rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
    
    tela.fill((255, 255, 255))
    pygame.display.flip()

pygame.quit() 