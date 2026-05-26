import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        self._choiceArrivo = None
        self._choicePartenza = None


    def handleAnalizza(self, e):
        cMinTxt = self._view._txtInCMin.value

        if cMinTxt == "":
            self._view._txtResults.controls.clear()
            self._view._txtResults.controls.append(ft.Text(
                "Inserire un valore numerico per numero minimo compagnie", color = "red"))
            self._view.update_page()

        try:
            cMinTxt = int(cMinTxt)
        except ValueError:
            self._view._txtResults.controls.clear()
            self._view._txtResults.controls.append(ft.Text(
                "Inserire un valore intero per numero minimo compagnie", color="red"))
            self._view.update_page()

        if cMinTxt <= 0:
            self._view._txtResults.controls.clear()
            self._view._txtResults.controls.append(ft.Text(
                "Inserire un valore maggiore di 0 per numero minimo compagnie", color="red"))
            self._view.update_page()

        self._model.buildGraph(cMinTxt)
        nNodes, nEdges = self._model.getGraphDetails()

        self._view._txtResults.controls.clear()
        self._view._txtResults.controls.append(ft.Text(
            "Grafo correttamente creato", color="green"))
        self._view._txtResults.controls.append(ft.Text(
            f"Il grafo contiene {nNodes} nodi e {nEdges} archi", color="green"))

        allNodes = self._model.getAllNodes()
        self.fillDD(allNodes)

        self._view.update_page()


    def handleConnessi(self, e):
        if self._choicePartenza is None:
            self._view._txtResults.controls.clear()
            self._view._txtResults.controls.append(ft.Text(
                "Attenzione, per usare questo metodo occorre selezionare un aeroporto di partenza",
            color="red"))
            self._view.update_page()
            return

        viciniT = self._model.getViciniOrdinati(self._choicePartenza)
        self._view._txtResults.controls.clear()
        for v in viciniT:
            self._view._txtResults.controls.append(ft.Text(f"{v[0]} - peso: {v[1]}"))
            self._view.update_page()


    def handleTestConnessione(self, e):
        if self._choicePartenza is None:
            self._view._txtResults.controls.clear()
            self._view._txtResults.controls.append(ft.Text(
                "Attenzione, per usare questo metodo occorre selezionare un aeroporto di partenza",
            color="red"))
            self._view.update_page()
            return

        if self._choiceArrivo is None:
            self._view._txtResults.controls.clear()
            self._view._txtResults.controls.append(ft.Text(
                "Attenzione, per usare questo metodo occorre selezionare un aeroporto di arrivo",
            color="red"))
            self._view.update_page()
            return

        if not self._model.hasPath(self._choicePartenza, self._choiceArrivo): # se non c'è un percorso tra i
            # due nodi
            self._view._txtResults.controls.clear()
            self._view._txtResults.controls.append(ft.Text(
                f"Non ho trovato un cammino tra {self._choicePartenza} e {self._choiceArrivo}",
            color="orange"))
            self._view.update_page()
            return

        path = self._model.getPath(self._choicePartenza, self._choiceArrivo)
        self._view._txtResults.controls.clear()
        self._view._txtResults.controls.append(ft.Text(f"Ho trovato un cammino fra "
                                                       f"{self._choicePartenza} e {self._choiceArrivo}",
                                                       color = "green"))
        self._view._txtResults.controls.append(ft.Text("Di seguito gli aeroporti connessi:"))
        for p in path:
            self._view._txtResults.controls.append(ft.Text(p))
        self._view.update_page()


    def handleCerca(self, e):
        t = self._view._txtInNTratteMax.value

        try:
            tInt = int(t)
        except ValueError:
            self._view._txtResults.controls.clear()
            self._view._txtResults.controls.append(ft.Text(f"Il valore di t deve essere un intero positivo"),
                                                   color = "red")
            return

        path, score = self._model.getCamminoOttimo(self._choicePartenza, self._choiceArrivo, tInt)
        self._view._txtResults.controls.clear()
        self._view._txtResults.controls.append(ft.Text(
            f"Cammino fra {self._choicePartenza} e {self._choiceArrivo} trovato", color = "green"))
        self._view._txtResults.controls.append(ft.Text(
            f"Il cammino ha uno score complessivo di {score} e contiene i seguenti nodi:", color = "green"))

        for p in path:
            self._view._txtResults.controls.append(ft.Text(p))
        self._view.update_page()


    def fillDD(self, allNodes):
        # recupero tutti i nodi del grafo e li metto nel dd
        for n in allNodes:
            self._view._ddAeroportoP.options.append(ft.dropdown.Option(data=n,
                                                                       key=n.IATA_CODE,
                                                                       on_click=self._choiceDDpartenza))

            self._view._ddAeroportoA.options.append(ft.dropdown.Option(data=n,
                                                                       key=n.IATA_CODE,
                                                                       on_click=self._choiceDDarrivo))


    def _choiceDDarrivo(self, e):
        self._choiceArrivo = e.control.data


    def _choiceDDpartenza(self, e):
        self._choicePartenza = e.control.data

