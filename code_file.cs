using System;

public interface IPrint
{
    void Print();
}

public class Geom_figures
{
    public virtual double Square()A
    {
        return 0;
    }
    public override string ToString()
    {
        return $"Площадь фигуры: {Square():F2}";
    }
}

public class Rectangle : Geom_figures, IPrint
{
    public double width { get; set; }
    public double height { get; set; }

    public Rectangle(double Width, double Height)
    {
        width = Width;
        height = Height;
    }

    public override double Square()
    {
        return width * height;
    }

    public override string ToString()
    {
        return $"Прямоугольник: длина = {height:F2}, ширина = {width:F2}, {base.ToString()}";
    }
    public void Print()
    {
        Console.WriteLine(this.ToString());
    }
}


public class Quadro : Rectangle, IPrint
{
    public Quadro(double Q_side) : base(Q_side, Q_side)
    {
    }
    public override string ToString()
    {
        return $"Квадрат: сторона = {width:F2}, {base.ToString()}";
    }
    public void Print()
    {
        Console.WriteLine(this.ToString());
    }
}


public class Circle : Geom_figures, IPrint
{
    public double radius { get; set; }

    public Circle(double Radius)
    {
        radius = Radius;
    }

    public override double Square()
    {
        return 3.14 * radius * radius;
    }

    public override string ToString()
    {
        return $"Окружность: радиус = {radius:F2}, {base.ToString()}";
    }

    public void Print()
    {
        Console.WriteLine(this.ToString());
    }
}


class Program
{

    static void Main()
    {
        Console.WriteLine("Введите параметры фигур:\n");

        double rectWidth = ReadDouble("Введите ширину прямоугольника: ");
        double rectHeight = ReadDouble("Введите длину прямоугольника: ");
        var rectangle = new Rectangle(rectWidth, rectHeight);

        double quadSide = ReadDouble("Введите сторону квадрата: ");
        var quadro = new Quadro(quadSide);

        double circRadius = ReadDouble("Введите радиус окружности: ");
        var circle = new Circle(circRadius);

        Geom_figures[] figures = { rectangle, quadro, circle };

        Console.WriteLine("\n=== Вывод через Print() ===");
        foreach (var figure in figures)
        {
            if (figure is IPrint printable)
            {
                printable.Print();
            }
        }

        Console.WriteLine("\nНажмите любую клавишу для выхода...");
        Console.ReadKey();
    }

    static double ReadDouble(string prompt)
    {
        double value;
        while (true)
        {
            Console.Write(prompt);
            string input = Console.ReadLine();

            if (double.TryParse(input, out value))
            {
                if (value > 0)
                {
                    return value;
                }
                else
                {
                    Console.WriteLine("Ошибка: значение должно быть положительным числом. Попробуйте снова.");
                }
            }
            else
            {
                Console.WriteLine("Ошибка: введите корректное число (например, 3.14 или 5).");
            }
        }
    }
}
