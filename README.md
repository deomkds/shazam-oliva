# Shazam-Oliva

Shazam-Oliva é um script que retorna o nome da música que está sendo tocada neste momento na [Rádio Verde Oliva](https://www.eb.mil.br/web/central-de-conteudos/radio-verde-oliva).

Ao receber a informação, o script anuncia, em voz alta, o nome da música e do intérprete. Também envia uma notificação para a área de trabalho (notify-send) e para todos os dispositivos pareados no [KDE Connect](https://kdeconnect.kde.org/).

### Observações

1. Caso queira consultar outra estação, altere a URL dentro do script mudando a variável `RADIO_URL`.
2. O script possui várias opções de personalização logo no topo que podem ser alteradas para uma melhor experiência.

### Bugs

Não que eu saiba, mas o script foi testado apenas na versão mais recente do Manjaro com KDE.

### Dependências Externas

1. [Selenium](https://www.selenium.dev/)
   1. Necessita instalação de um driver. Por padrão, o script usa o driver `GECKO`.
2. [Lingua](https://pypi.org/project/lingua-language-detector/)
   1. O pacote correto no PyPI é o `lingua-language-detector`.
3. [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
4. [gTTS](https://pypi.org/project/gTTS/)
5. [pydub](https://pypi.org/project/pydub/)

Também pode tentar:

`pip install -r requirements.txt`
