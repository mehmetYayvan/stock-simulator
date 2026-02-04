from setuptools import setup, find_packages

setup(
    name="stock-simulator",
    version="1.0.0",
    description="Simulate historical stock investments",
    author="Your Name",
    packages=find_packages(),
    package_dir={"": "."},
    py_modules=["src.cli", "src.fetcher", "src.simulator"],
    install_requires=[
        "yfinance>=0.2.0",
        "click>=8.0.0",
        "pandas>=1.5.0",
    ],
    entry_points={
        "console_scripts": [
            "stock-sim=src.cli:cli",
        ],
    },
    python_requires=">=3.10",
)
