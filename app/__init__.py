"""Pacote principal do Controle de Ponto Potiguar.

A aplicação Flask é criada exclusivamente por ``main.create_app``.
Manter este módulo sem efeitos colaterais permite que scripts operacionais,
como backup e restauração, importem a infraestrutura sem carregar rotas,
modelos de reconhecimento facial ou criar diretórios inesperados.
"""
