
class elasticsearch:
    def setCocktailName(self, cocktailList):
        self.cocktailList = cocktailList




if __name__ == '__main__':
    cocktail = ['Alexander', 'Aviation', 'B-52', 'Bacardi']

    elastic = elasticsearch()

    elastic.setCocktailName(cocktail)

    elastic.howToMake()