# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/numpy-tutorials/content/tutorial-nlp-from-scratch.md

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[numpy_speaches]'

import numpy as np
import pandas as pd
import pooch
import string
import re
import zipfile
import os


class TextPreprocess:
    """Text Preprocessing for a Natural Language Processing model."""

    def txt_to_df(self, file):
        """Function to convert a txt file to pandas dataframe.

        Parameters
        ----------
        file : str
            Path to the txt file.

        Returns
        -------
        Pandas dataframe
            txt file converted to a dataframe.

        """
        with open(imdb_train, "r") as in_file:
            stripped = (line.strip() for line in in_file)
            reviews = {}
            for line in stripped:
                lines = [splits for splits in line.split("\t") if splits != ""]
                reviews[lines[1]] = float(lines[0])
        df = pd.DataFrame(reviews.items(), columns=["review", "sentiment"])
        df = df.sample(frac=1).reset_index(drop=True)
        return df

    def unzipper(self, zipped, to_extract):
        """Function to extract a file from a zipped folder.

        Parameters
        ----------
        zipped : str
            Path to the zipped folder.

        to_extract: str
            Path to the file to be extracted from the zipped folder

        Returns
        -------
        str
            Path to the extracted file.

        """
        fh = open(zipped, "rb")
        z = zipfile.ZipFile(fh)
        outdir = os.path.split(zipped)[0]
        z.extract(to_extract, outdir)
        fh.close()
        output_file = os.path.join(outdir, to_extract)
        return output_file

    def cleantext(self, df, text_column=None, remove_stopwords=True, remove_punc=True):
        """Function to clean text data.

        Parameters
        ----------
        df : pandas dataframe
            The dataframe housing the input data.
        text_column : str
            Column in dataframe whose text is to be cleaned.
        remove_stopwords : bool
            if True, remove stopwords from text
        remove_punc : bool
            if True, remove punctuation symbols from text

        Returns
        -------
        Numpy array
            Cleaned text.

        """
        df[text_column] = df[text_column].str.lower()
        stopwords = [
            "a",
            "about",
            "above",
            "after",
            "again",
            "against",
            "all",
            "am",
            "an",
            "and",
            "any",
            "are",
            "as",
            "at",
            "be",
            "because",
            "been",
            "before",
            "being",
            "below",
            "between",
            "both",
            "but",
            "by",
            "could",
            "did",
            "do",
            "does",
            "doing",
            "down",
            "during",
            "each",
            "few",
            "for",
            "from",
            "further",
            "had",
            "has",
            "have",
            "having",
            "he",
            "he'd",
            "he'll",
            "he's",
            "her",
            "here",
            "here's",
            "hers",
            "herself",
            "him",
            "himself",
            "his",
            "how",
            "how's",
            "i",
            "i'd",
            "i'll",
            "i'm",
            "i've",
            "if",
            "in",
            "into",
            "is",
            "it",
            "it's",
            "its",
            "itself",
            "let's",
            "me",
            "more",
            "most",
            "my",
            "myself",
            "nor",
            "of",
            "on",
            "once",
            "only",
            "or",
            "other",
            "ought",
            "our",
            "ours",
            "ourselves",
            "out",
            "over",
            "own",
            "same",
            "she",
            "she'd",
            "she'll",
            "she's",
            "should",
            "so",
            "some",
            "such",
            "than",
            "that",
            "that's",
            "the",
            "their",
            "theirs",
            "them",
            "themselves",
            "then",
            "there",
            "there's",
            "these",
            "they",
            "they'd",
            "they'll",
            "they're",
            "they've",
            "this",
            "those",
            "through",
            "to",
            "too",
            "under",
            "until",
            "up",
            "very",
            "was",
            "we",
            "we'd",
            "we'll",
            "we're",
            "we've",
            "were",
            "what",
            "what's",
            "when",
            "when's",
            "where",
            "where's",
            "which",
            "while",
            "who",
            "who's",
            "whom",
            "why",
            "why's",
            "with",
            "would",
            "you",
            "you'd",
            "you'll",
            "you're",
            "you've",
            "your",
            "yours",
            "yourself",
            "yourselves",
        ]

        def remove_stopwords(data, column):
            data[f"{column} without stopwords"] = data[column].apply(
                lambda x: " ".join(
                    [word for word in x.split() if word not in stopwords]
                )
            )
            return data

        def remove_tags(string):
            result = re.sub("<*>", "", string)
            return result

        if remove_stopwords:
            data_without_stopwords = remove_stopwords(df, text_column)
            data_without_stopwords[f"clean_{text_column}"] = data_without_stopwords[
                f"{text_column} without stopwords"
            ].apply(lambda cw: remove_tags(cw))
        if remove_punc:
            data_without_stopwords[f"clean_{text_column}"] = data_without_stopwords[
                f"clean_{text_column}"
            ].str.replace("[{}]".format(string.punctuation), " ", regex=True)
        X = data_without_stopwords[f"clean_{text_column}"].to_numpy()
        return X

    def sent_tokeniser(self, x):
        """Function to split text into sentences.

        Parameters
        ----------
        x : str
            piece of text

        Returns
        -------
        list
            sentences with punctuation removed.

        """
        sentences = re.split("(?<!\\w\\.\\w.)(?<![A-Z][a-z]\\.)(?<=\\.|\\?)\\s", x)
        sentences.pop()
        sentences_cleaned = [re.sub("[^\\w\\s]", "", x) for x in sentences]
        return sentences_cleaned

    def word_tokeniser(self, text):
        """Function to split text into tokens.

        Parameters
        ----------
        x : str
            piece of text

        Returns
        -------
        list
            words with punctuation removed.

        """
        tokens = re.split("([-\\s.,;!?])+", text)
        words = [x for x in tokens if x not in "- \t\n.,;!?\\" and "\\" not in x]
        return words

    def loadGloveModel(self, emb_path):
        """Function to read from the word embedding file.

        Returns
        -------
        Dict
            mapping from word to corresponding word embedding.

        """
        print("Loading Glove Model")
        File = emb_path
        f = open(File, "r")
        gloveModel = {}
        for line in f:
            splitLines = line.split()
            word = splitLines[0]
            wordEmbedding = np.array([float(value) for value in splitLines[1:]])
            gloveModel[word] = wordEmbedding
        print(len(gloveModel), " words loaded!")
        return gloveModel

    def text_to_paras(self, text, para_len):
        """Function to split text into paragraphs.

        Parameters
        ----------
        text : str
            piece of text

        para_len : int
            length of each paragraph

        Returns
        -------
        list
            paragraphs of specified length.

        """
        words = text.split()
        no_paras = int(np.ceil(len(words) / para_len))
        sentences = self.sent_tokeniser(text)
        k, m = divmod(len(sentences), no_paras)
        agg_sentences = [
            sentences[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
            for i in range(no_paras)
        ]
        paras = np.array([" ".join(sents) for sents in agg_sentences])
        return paras


data = pooch.create(
    path=pooch.os_cache("numpy-nlp-tutorial"),
    base_url="",
    registry={
        "imdb_train.txt": "6a38ea6ab5e1902cc03f6b9294ceea5e8ab985af991f35bcabd301a08ea5b3f0",
        "imdb_test.txt": "7363ef08ad996bf4233b115008d6d7f9814b7cc0f4d13ab570b938701eadefeb",
        "glove.6B.50d.zip": "617afb2fe6cbd085c235baf7a465b96f4112bd7f7ccb2b2cbd649fed9cbcf2fb",
    },
    urls={
        "imdb_train.txt": "doi:10.5281/zenodo.4117827/imdb_train.txt",
        "imdb_test.txt": "doi:10.5281/zenodo.4117827/imdb_test.txt",
        "glove.6B.50d.zip": "https://nlp.stanford.edu/data/glove.6B.zip",
    },
)
imdb_train = data.fetch("imdb_train.txt")
textproc = TextPreprocess()
train_df = textproc.txt_to_df(imdb_train)
X_train = textproc.cleantext(
    train_df, text_column="review", remove_stopwords=True, remove_punc=True
)[0:2000]
y_train = train_df["sentiment"].to_numpy()[0:2000]
speech_data_path = "tutorial-nlp-from-scratch/speeches.csv"
speech_df = pd.read_csv(speech_data_path)
X_pred = textproc.cleantext(
    speech_df, text_column="speech", remove_stopwords=True, remove_punc=False
)
speakers = speech_df["speaker"].to_numpy()
glove = data.fetch("glove.6B.50d.zip")
emb_path = textproc.unzipper(glove, "glove.6B.300d.txt")
emb_matrix = textproc.loadGloveModel(emb_path)


def initialise_params(hidden_dim, input_dim):
    Wf = np.random.randn(hidden_dim, hidden_dim + input_dim)
    bf = np.random.randn(hidden_dim, 1)
    Wi = np.random.randn(hidden_dim, hidden_dim + input_dim)
    bi = np.random.randn(hidden_dim, 1)
    Wcm = np.random.randn(hidden_dim, hidden_dim + input_dim)
    bcm = np.random.randn(hidden_dim, 1)
    Wo = np.random.randn(hidden_dim, hidden_dim + input_dim)
    bo = np.random.randn(hidden_dim, 1)
    W2 = np.random.randn(1, hidden_dim)
    b2 = np.zeros((1, 1))
    parameters = {
        "Wf": Wf,
        "bf": bf,
        "Wi": Wi,
        "bi": bi,
        "Wcm": Wcm,
        "bcm": bcm,
        "Wo": Wo,
        "bo": bo,
        "W2": W2,
        "b2": b2,
    }
    return parameters


def sigmoid(x):
    n = np.exp(np.fmin(x, 0))
    d = 1 + np.exp(-np.abs(x))
    return n / d


def fp_forget_gate(concat, parameters):
    ft = sigmoid(np.dot(parameters["Wf"], concat) + parameters["bf"])
    return ft


def fp_input_gate(concat, parameters):
    it = sigmoid(np.dot(parameters["Wi"], concat) + parameters["bi"])
    cmt = np.tanh(np.dot(parameters["Wcm"], concat) + parameters["bcm"])
    return it, cmt


def fp_output_gate(concat, next_cs, parameters):
    ot = sigmoid(np.dot(parameters["Wo"], concat) + parameters["bo"])
    next_hs = ot * np.tanh(next_cs)
    return ot, next_hs


def fp_fc_layer(last_hs, parameters):
    z2 = np.dot(parameters["W2"], last_hs) + parameters["b2"]
    a2 = sigmoid(z2)
    return a2


def forward_prop(X_vec, parameters, input_dim):
    hidden_dim = parameters["Wf"].shape[0]
    time_steps = len(X_vec)
    prev_hs = np.zeros((hidden_dim, 1))
    prev_cs = np.zeros(prev_hs.shape)
    caches = {"lstm_values": [], "fc_values": []}
    for t in range(time_steps):
        x = X_vec[t]
        xt = emb_matrix.get(x, np.random.rand(input_dim, 1))
        xt = xt.reshape((input_dim, 1))
        concat = np.vstack((prev_hs, xt))
        ft = fp_forget_gate(concat, parameters)
        it, cmt = fp_input_gate(concat, parameters)
        io = it * cmt
        next_cs = ft * prev_cs + io
        ot, next_hs = fp_output_gate(concat, next_cs, parameters)
        lstm_cache = {
            "next_hs": next_hs,
            "next_cs": next_cs,
            "prev_hs": prev_hs,
            "prev_cs": prev_cs,
            "ft": ft,
            "it": it,
            "cmt": cmt,
            "ot": ot,
            "xt": xt,
        }
        caches["lstm_values"].append(lstm_cache)
        prev_hs = next_hs
        prev_cs = next_cs
    a2 = fp_fc_layer(next_hs, parameters)
    fc_cache = {"a2": a2, "W2": parameters["W2"]}
    caches["fc_values"].append(fc_cache)
    return caches


def initialize_grads(parameters):
    grads = {}
    for param in parameters.keys():
        grads[f"d{param}"] = np.zeros(parameters[param].shape)
    return grads


def bp_forget_gate(hidden_dim, concat, dh_prev, dc_prev, cache, gradients, parameters):
    dft = (
        (
            dc_prev * cache["prev_cs"]
            + cache["ot"]
            * (1 - np.square(np.tanh(cache["next_cs"])))
            * cache["prev_cs"]
            * dh_prev
        )
        * cache["ft"]
        * (1 - cache["ft"])
    )
    gradients["dWf"] += np.dot(dft, concat.T)
    gradients["dbf"] += np.sum(dft, axis=1, keepdims=True)
    dh_f = np.dot(parameters["Wf"][:, :hidden_dim].T, dft)
    return dh_f, gradients


def bp_input_gate(hidden_dim, concat, dh_prev, dc_prev, cache, gradients, parameters):
    dit = (
        (
            dc_prev * cache["cmt"]
            + cache["ot"]
            * (1 - np.square(np.tanh(cache["next_cs"])))
            * cache["cmt"]
            * dh_prev
        )
        * cache["it"]
        * (1 - cache["it"])
    )
    dcmt = (
        dc_prev * cache["it"]
        + cache["ot"]
        * (1 - np.square(np.tanh(cache["next_cs"])))
        * cache["it"]
        * dh_prev
    ) * (1 - np.square(cache["cmt"]))
    gradients["dWi"] += np.dot(dit, concat.T)
    gradients["dWcm"] += np.dot(dcmt, concat.T)
    gradients["dbi"] += np.sum(dit, axis=1, keepdims=True)
    gradients["dbcm"] += np.sum(dcmt, axis=1, keepdims=True)
    dh_i = np.dot(parameters["Wi"][:, :hidden_dim].T, dit)
    dh_cm = np.dot(parameters["Wcm"][:, :hidden_dim].T, dcmt)
    return dh_i, dh_cm, gradients


def bp_output_gate(hidden_dim, concat, dh_prev, dc_prev, cache, gradients, parameters):
    dot = dh_prev * np.tanh(cache["next_cs"]) * cache["ot"] * (1 - cache["ot"])
    gradients["dWo"] += np.dot(dot, concat.T)
    gradients["dbo"] += np.sum(dot, axis=1, keepdims=True)
    dh_o = np.dot(parameters["Wo"][:, :hidden_dim].T, dot)
    return dh_o, gradients


def bp_fc_layer(target, caches, gradients):
    predicted = np.array(caches["fc_values"][0]["a2"])
    target = np.array(target)
    dZ2 = predicted - target
    last_hs = caches["lstm_values"][-1]["next_hs"]
    gradients["dW2"] = np.dot(dZ2, last_hs.T)
    gradients["db2"] = np.sum(dZ2)
    W2 = caches["fc_values"][0]["W2"]
    dh_last = np.dot(W2.T, dZ2)
    return dh_last, gradients


def backprop(y, caches, hidden_dim, input_dim, time_steps, parameters):
    gradients = initialize_grads(parameters)
    dh_last, gradients = bp_fc_layer(target, caches, gradients)
    dh_prev = dh_last
    dc_prev = np.zeros(dh_prev.shape)
    for t in reversed(range(time_steps)):
        cache = caches["lstm_values"][t]
        concat = np.concatenate((cache["prev_hs"], cache["xt"]), axis=0)
        dh_f, gradients = bp_forget_gate(
            hidden_dim, concat, dh_prev, dc_prev, cache, gradients, parameters
        )
        dh_i, dh_cm, gradients = bp_input_gate(
            hidden_dim, concat, dh_prev, dc_prev, cache, gradients, parameters
        )
        dh_o, gradients = bp_output_gate(
            hidden_dim, concat, dh_prev, dc_prev, cache, gradients, parameters
        )
        dh_prev = dh_f + dh_i + dh_cm + dh_o
        dc_prev = (
            dc_prev * cache["ft"]
            + cache["ot"]
            * (1 - np.square(np.tanh(cache["next_cs"])))
            * cache["ft"]
            * dh_prev
        )
    return gradients


def initialise_mav(hidden_dim, input_dim, params):
    v = {}
    s = {}
    for key in params:
        v["d" + key] = np.zeros(params[key].shape)
        s["d" + key] = np.zeros(params[key].shape)
    return v, s


def update_parameters(
    parameters, gradients, v, s, learning_rate=0.01, beta1=0.9, beta2=0.999
):
    for key in parameters:
        v["d" + key] = beta1 * v["d" + key] + (1 - beta1) * gradients["d" + key]
        s["d" + key] = beta2 * s["d" + key] + (1 - beta2) * gradients["d" + key] ** 2
        parameters[key] = parameters[key] - learning_rate * v["d" + key] / np.sqrt(
            s["d" + key] + 1e-08
        )
    return parameters, v, s


hidden_dim = 64
input_dim = emb_matrix["memory"].shape[0]
learning_rate = 0.001
epochs = 10
parameters = initialise_params(hidden_dim, input_dim)
v, s = initialise_mav(hidden_dim, input_dim, parameters)
for epoch in range(epochs):
    for sample, target in zip(X_train, y_train):
        b = textproc.word_tokeniser(sample)
        caches = forward_prop(b, parameters, input_dim)
        gradients = backprop(target, caches, hidden_dim, input_dim, len(b), parameters)
        parameters, v, s = update_parameters(
            parameters,
            gradients,
            v,
            s,
            learning_rate=learning_rate,
            beta1=0.999,
            beta2=0.9,
        )
np.save("tutorial-nlp-from-scratch/parameters.npy", parameters)
