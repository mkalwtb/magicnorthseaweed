from matplotlib import pyplot as plt
from plotting import plot_forecast, save_to_web
from spots import SPOTS, ijmuiden
from tabulate import tabulate
import openai

messages = [ {"role": "system", "content": "Je bent een Nederlandse surf voorspeller."} ]
openai.api_key = "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"

opdracht = "Schrijf een aanbeveling voor wanneer men moet gaan golf surfen, op basis van de volgende gegevens. De rating bepaald via een surf AI. Die is leidend en geeft aan hoe goed de surf is.  Als de surf hoger dan een 6 is, wil je gaan surfen. Gebruik 'alert' als de rating hoger dan 8 is. Geef ook aan hoe op welke dag en hoe laat je moet gaan surfen. Geef aan of de golfen hoog zijn, en of het stormachtig of rustig is. Dit is over Zandvoort. Wees iets creatiever in je woordkeuze. Schrijf 1 paragraaf zonder bullet points etc."


if __name__ == '__main__':
    data = ijmuiden.surf_rating(cache=True)
    # print(tabulate(data, headers='keys', tablefmt='psql'))
    plt.show()

    while True:
        message = input("User : ")
        if message:
            messages.append(
                {"role": "user", "content": message},
            )
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )

        reply = chat.choices[0].message.content
        print(f"ChatGPT: {reply}")
        messages.append({"role": "assistant", "content": reply})
