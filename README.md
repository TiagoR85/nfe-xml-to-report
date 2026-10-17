# nfe-xml-to-report

[![ci](https://github.com/TiagoR85/nfe-xml-to-report/actions/workflows/ci.yml/badge.svg)](https://github.com/TiagoR85/nfe-xml-to-report/actions/workflows/ci.yml)
[![release](https://img.shields.io/github/v/release/TiagoR85/nfe-xml-to-report)](https://github.com/TiagoR85/nfe-xml-to-report/releases)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Pipeline didático de XML de NF-e 4.00: validação em Python (lxml) + relatórios Excel/PDF em C# (dotnet tool).

## About this repository

CLI Python valida um diretório de XMLs de NF-e (XSD + regras semânticas) e invoca um dotnet tool que gera um Excel consolidado e um PDF DANFE-simplificado por NF-e.
