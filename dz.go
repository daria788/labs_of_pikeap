package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"regexp"
	"strings"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

type Character struct {
	NameEN      string      `json:"name_en"`
	NameRU      string      `json:"name_ru"`
	Role        string      `json:"role"`
	Weapon      string      `json:"weapon"`
	ArtifactSet interface{} `json:"artifact_set"`
	Pieces      interface{} `json:"pieces"`
	Sands       string      `json:"sands"`
	Goblet      string      `json:"goblet"`
	Circlet     string      `json:"circlet"`
}

var (
	botToken   = "8374734234:AAFf66s_UYrJyfMxt_jgQwmuyXoWKxQhh4M"
	characters map[string]Character
	aliases    map[string]string
	userStates = make(map[string]string)
	favorites  = make(map[int64][]string)
)

const (
	StateWaitingForCharacter = "waiting_for_character"
	StateWaitingForCompare1  = "waiting_for_compare_1"
	StateWaitingForCompare2  = "waiting_for_compare_2"
)

// === Нормализация: убираем всё, кроме букв и цифр ===
func normalize(s string) string {
	reg := regexp.MustCompile(`[^a-zA-Zа-яА-Я0-9]`)
	return strings.ToLower(reg.ReplaceAllString(s, ""))
}

func main() {
	bot, err := tgbotapi.NewBotAPI(botToken)
	if err != nil {
		log.Fatal("❌ Не удалось создать бота:", err)
	}
	bot.Debug = false
	log.Printf("✅ Бот запущен как @%s", bot.Self.UserName)

	loadConfig()

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60
	updates := bot.GetUpdatesChan(u)

	for update := range updates {
		if update.Message != nil {
			handleMessage(bot, update.Message)
		}
	}
}

func loadConfig() {
	data, err := os.ReadFile("config.json")
	if err != nil {
		log.Fatal("❌ Не найден config.json")
	}

	var cfg struct {
		Characters map[string]Character `json:"characters"`
		Aliases    map[string]string    `json:"aliases"`
	}
	if err := json.Unmarshal(data, &cfg); err != nil {
		log.Fatal("❌ Ошибка парсинга config.json:", err)
	}

	characters = cfg.Characters
	aliases = cfg.Aliases
	log.Printf("✅ Загружено персонажей: %d", len(characters))
}

// === НАДЕЖНЫЙ ПОИСК ПЕРСОНАЖА ===
func findCharacter(query string) (key string, c *Character) {
	q := normalize(query)

	// По ключу
	if c, ok := characters[q]; ok {
		return q, &c
	}

	// По алиасу
	if realKey, ok := aliases[q]; ok {
		if c, ok := characters[realKey]; ok {
			return realKey, &c
		}
	}

	// По имени
	for k, char := range characters {
		if normalize(char.NameEN) == q || normalize(char.NameRU) == q {
			return k, &char
		}
	}

	return "", nil
}

func handleMessage(bot *tgbotapi.BotAPI, msg *tgbotapi.Message) {
	chatID := msg.Chat.ID
	text := strings.TrimSpace(msg.Text)
	chatIDStr := fmt.Sprint(chatID)

	if text == "/start" || text == "/hello" {
		start(bot, msg)
		return
	}
	if text == "/fav" {
		showFavorites(bot, msg)
		return
	}
	if strings.HasPrefix(text, "/compare ") {
		compareCommand(bot, msg, text[9:])
		return
	}
	if strings.HasPrefix(text, "⭐") {
		name := strings.TrimSpace(strings.TrimPrefix(text, "⭐"))
		if name != "" {
			addToFavorites(bot, msg, name)
			return
		}
	}

	// Состояние: ожидание второго персонажа
	if userStates[chatIDStr] == StateWaitingForCompare2 {
		if text == "🔙 Вернуться в меню" {
			delete(userStates, chatIDStr)
			delete(userStates, chatIDStr+"_char1")
			sendMessageWithKeyboard(bot, chatID, "Возврат в меню", menuKeyboard())
			return
		}
		first := userStates[chatIDStr+"_char1"]
		_, c1 := findCharacter(first)
		_, c2 := findCharacter(text)
		if c1 != nil && c2 != nil {
			doCompare(bot, msg, *c1, *c2)
		} else {
			bot.Send(tgbotapi.NewMessage(chatID, "❌ Один из персонажей не найден."))
		}
		delete(userStates, chatIDStr)
		delete(userStates, chatIDStr+"_char1")
		sendMessageWithKeyboard(bot, chatID, "Возврат в меню", menuKeyboard())
		return
	}

	// Состояние: ожидание первого персонажа для сравнения
	if userStates[chatIDStr] == StateWaitingForCompare1 {
		if text == "🔙 Вернуться в меню" {
			delete(userStates, chatIDStr)
			sendMessageWithKeyboard(bot, chatID, "Возврат в меню", menuKeyboard())
			return
		}
		_, c := findCharacter(text)
		if c == nil {
			bot.Send(tgbotapi.NewMessage(chatID, "❌ Персонаж не найден. Попробуйте ещё раз."))
			return
		}
		userStates[chatIDStr] = StateWaitingForCompare2
		userStates[chatIDStr+"_char1"] = text
		msgConf := tgbotapi.NewMessage(chatID, fmt.Sprintf("✅ Выбран: *%s*\nВведите имя второго персонажа:", c.NameRU))
		msgConf.ParseMode = "Markdown"
		msgConf.ReplyMarkup = backKeyboard()
		bot.Send(msgConf)
		return
	}

	// Состояние: ожидание персонажа для сборки
	if userStates[chatIDStr] == StateWaitingForCharacter {
		if text == "🔙 Вернуться в меню" {
			delete(userStates, chatIDStr)
			sendMessageWithKeyboard(bot, chatID, "Возврат в меню", menuKeyboard())
			return
		}
		showBuild(bot, msg, text)
		return
	}

	// Главное меню
	switch text {
	case "⚡ О боте ⚡":
		about(bot, msg)
	case "🌟 Избранное":
		showFavorites(bot, msg)
	case "Артефакты персонажей":
		userStates[chatIDStr] = StateWaitingForCharacter
		msgConf := tgbotapi.NewMessage(chatID, "Введите имя персонажа (например: *Аяка*, *Ху Тао*, *Сяо*):")
		msgConf.ParseMode = "Markdown"
		msgConf.ReplyMarkup = backKeyboard()
		bot.Send(msgConf)
	case "🆚 Сравнить персонажей":
		userStates[chatIDStr] = StateWaitingForCompare1
		msgConf := tgbotapi.NewMessage(chatID, "Введите имя первого персонажа:")
		msgConf.ParseMode = "Markdown"
		msgConf.ReplyMarkup = backKeyboard()
		bot.Send(msgConf)
	case "↩️ Выход ↩️":
		msgConf := tgbotapi.NewMessage(chatID, "До новых встреч! 👋")
		msgConf.ReplyMarkup = tgbotapi.NewRemoveKeyboard(true)
		bot.Send(msgConf)
	case "🔙 Вернуться в меню":
		delete(userStates, chatIDStr)
		delete(userStates, chatIDStr+"_char1")
		sendMessageWithKeyboard(bot, chatID, "Возврат в меню", menuKeyboard())
	default:
		sendMessageWithKeyboard(bot, chatID, "Пожалуйста, используйте кнопки меню.", menuKeyboard())
	}
}

func sendMessageWithKeyboard(bot *tgbotapi.BotAPI, chatID int64, text string, keyboard interface{}) {
	msg := tgbotapi.NewMessage(chatID, text)
	msg.ReplyMarkup = keyboard
	bot.Send(msg)
}

func menuKeyboard() tgbotapi.ReplyKeyboardMarkup {
	return tgbotapi.NewReplyKeyboard(
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("⚡ О боте ⚡"),
			tgbotapi.NewKeyboardButton("🌟 Избранное"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("Артефакты персонажей"),
			tgbotapi.NewKeyboardButton("🆚 Сравнить персонажей"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("↩️ Выход ↩️"),
		),
	)
}

func backKeyboard() tgbotapi.ReplyKeyboardMarkup {
	return tgbotapi.NewReplyKeyboard(
		tgbotapi.NewKeyboardButtonRow(tgbotapi.NewKeyboardButton("🔙 Вернуться в меню")),
	)
}

func start(bot *tgbotapi.BotAPI, msg *tgbotapi.Message) {
	text := fmt.Sprintf(
		"Привет, %s! 👋\n"+
			"Я помогу собрать персонажей в Genshin Impact.\n"+
			"• Нажмите Артефакты персонажей, чтобы найти сборку.\n"+
			"• Сохраняйте любимых в Избранное (⭐ Имя).\n"+
			"• Используйте Сравнить, чтобы выбрать лучшего.",
		msg.From.FirstName,
	)
	sendMessageWithKeyboard(bot, msg.Chat.ID, text, menuKeyboard())
}

func about(bot *tgbotapi.BotAPI, msg *tgbotapi.Message) {
	sendMessageWithKeyboard(bot, msg.Chat.ID,
		"🤖 Бот создан для помощи в сборке персонажей Genshin Impact.\n\n"+
			"Данные взяты с https://genshin.gg/builds/",
		menuKeyboard())
}

func showBuild(bot *tgbotapi.BotAPI, msg *tgbotapi.Message, query string) {
	_, c := findCharacter(query)
	if c == nil {
		bot.Send(tgbotapi.NewMessage(msg.Chat.ID, "❌ Персонаж не найден. Попробуйте: *Аяка*, *Ху Тао*, *Сяо*, *Путешественник (Анемо)* и т.д."))
		return
	}

	var artifactLine string
	switch v := c.ArtifactSet.(type) {
	case string:
		artifactLine = v
	case []interface{}:
		parts := make([]string, len(v))
		for i, p := range v {
			if s, ok := p.(string); ok {
				parts[i] = s
			} else {
				parts[i] = fmt.Sprintf("%v", p)
			}
		}
		artifactLine = strings.Join(parts, " + ")
	default:
		artifactLine = "неизвестно"
	}

	var piecesLine string
	switch v := c.Pieces.(type) {
	case float64:
		piecesLine = fmt.Sprintf("%.0f шт.", v)
	case []interface{}:
		if len(v) >= 2 {
			p1 := v[0].(float64)
			p2 := v[1].(float64)
			piecesLine = fmt.Sprintf("%.0f + %.0f шт.", p1, p2)
		} else {
			piecesLine = "данные отсутствуют"
		}
	default:
		piecesLine = "данные отсутствуют"
	}

	reply := fmt.Sprintf(
		"✨ *%s* (%s) — _%s_\n\n"+
			"⚔️ *Оружие*: %s\n"+
			"🛡️ *Сет*: %s (%s)\n\n"+
			"🔮 *Статы*:\n"+
			"• Пески: %s\n"+
			"• Кубок: %s\n"+
			"• Тиара: %s",
		c.NameEN, c.NameRU, c.Role,
		c.Weapon, artifactLine, piecesLine,
		c.Sands, c.Goblet, c.Circlet,
	)

	msgConf := tgbotapi.NewMessage(msg.Chat.ID, reply)
	msgConf.ParseMode = "Markdown"
	msgConf.ReplyMarkup = backKeyboard()
	bot.Send(msgConf)
}

func addToFavorites(bot *tgbotapi.BotAPI, msg *tgbotapi.Message, query string) {
	chatID := msg.Chat.ID
	key, c := findCharacter(query)
	if c == nil {
		bot.Send(tgbotapi.NewMessage(chatID, "❌ Персонаж не найден. Проверьте написание."))
		return
	}
	for _, k := range favorites[chatID] {
		if k == key {
			bot.Send(tgbotapi.NewMessage(chatID, fmt.Sprintf("✨ %s уже в избранном!", c.NameRU)))
			return
		}
	}
	favorites[chatID] = append(favorites[chatID], key)
	bot.Send(tgbotapi.NewMessage(chatID, fmt.Sprintf("✅ %s добавлен(а) в избранное!", c.NameRU)))
}

func showFavorites(bot *tgbotapi.BotAPI, msg *tgbotapi.Message) {
	chatID := msg.Chat.ID
	list := favorites[chatID]
	if len(list) == 0 {
		bot.Send(tgbotapi.NewMessage(chatID, "Ваше избранное пусто. Добавьте персонажа: ⭐ Имя"))
		return
	}
	var lines []string
	for _, key := range list {
		if c, ok := characters[key]; ok {
			lines = append(lines, fmt.Sprintf("• %s (%s)", c.NameRU, c.Role))
		}
	}
	bot.Send(tgbotapi.NewMessage(chatID, "🌟 Ваше избранное:\n"+strings.Join(lines, "\n")))
}

func compareCommand(bot *tgbotapi.BotAPI, msg *tgbotapi.Message, args string) {
	parts := strings.Split(strings.ToLower(args), " и ")
	if len(parts) != 2 {
		bot.Send(tgbotapi.NewMessage(msg.Chat.ID,
			"❗ Формат: /compare Имя1 и Имя2\nПример: /compare Аяка и Ху Тао"))
		return
	}
	_, c1 := findCharacter(parts[0])
	_, c2 := findCharacter(parts[1])
	if c1 == nil || c2 == nil {
		bot.Send(tgbotapi.NewMessage(msg.Chat.ID, "❌ Один из персонажей не найден."))
		return
	}
	doCompare(bot, msg, *c1, *c2)
}

func doCompare(bot *tgbotapi.BotAPI, msg *tgbotapi.Message, c1, c2 Character) {
	format := func(c Character) string {
		artifact := ""
		switch v := c.ArtifactSet.(type) {
		case string:
			artifact = v
		case []interface{}:
			parts := make([]string, len(v))
			for i, p := range v {
				if s, ok := p.(string); ok {
					parts[i] = s
				} else {
					parts[i] = fmt.Sprintf("%v", p)
				}
			}
			artifact = strings.Join(parts, " + ")
		default:
			artifact = "неизвестно"
		}
		return fmt.Sprintf("%s (%s)\nОружие: %s\nСет: %s", c.NameRU, c.Role, c.Weapon, artifact)
	}
	reply := "🆚 Сравнение:\n\n🔵 " + format(c1) + "\n\n🔴 " + format(c2)
	bot.Send(tgbotapi.NewMessage(msg.Chat.ID, reply))
}
