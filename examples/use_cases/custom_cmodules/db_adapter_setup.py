from distutils.core import Extension, setup


def main():
    setup(
        name="DBAdapters",
        version="1.0.0",
        description="Custom DBAdapters module in python",
        author="Shardul",
        author_email="shardul@linea.ai",
        ext_modules=[Extension("DBAdapters", ["db_adapter.c"])],
    )


if __name__ == "__main__":
    main()
