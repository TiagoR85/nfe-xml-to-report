from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nfe_cli.validator import validar_dir


class _Parser(argparse.ArgumentParser):
    def error(self, message: str):  # exit code 1 para erros de uso
        self.print_usage(sys.stderr)
        print(f"erro: {message}", file=sys.stderr)
        raise SystemExit(1)


def _criar_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="nfecli")
    sub = parser.add_subparsers(dest="comando")

    p_validate = sub.add_parser("validate", help="valida XMLs de NF-e num diretorio")
    p_validate.add_argument("--in", dest="dir_in", required=True)
    p_validate.add_argument("--schemas", default=None)

    p_process = sub.add_parser("process", help="valida e gera relatorios")
    p_process.add_argument("--in", dest="dir_in", required=True)
    p_process.add_argument("--out", dest="dir_out", required=True)
    p_process.add_argument("--format", choices=("excel", "pdf", "all"), default="all")
    p_process.add_argument("--tool-path", default=None)
    p_process.add_argument("--schemas", default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _criar_parser()
    args = parser.parse_args(argv)

    if not args.comando:
        parser.print_usage(sys.stderr)
        return 1

    dir_in = Path(args.dir_in)
    if not dir_in.is_dir():
        print(f"erro: diretorio inexistente: {dir_in}", file=sys.stderr)
        return 1
    if not list(dir_in.glob("*.xml")):
        print(f"erro: nenhum .xml em {dir_in}", file=sys.stderr)
        return 1

    schemas = Path(args.schemas) if args.schemas else None
    erros = validar_dir(dir_in, schemas)
    if erros:
        for nome, codigo, mensagem in erros:
            print(f"{nome}:{codigo}: {mensagem}", file=sys.stderr)
        return 2

    n = len(list(dir_in.glob("*.xml")))
    if args.comando == "validate":
        print(f"OK: {n} NF-e validas")
        return 0

    from nfe_cli.runner import executar_tool

    codigo = executar_tool(dir_in, Path(args.dir_out), args.format, args.tool_path)
    if codigo != 0:
        print(f"erro: nfe-report terminou com exit {codigo}", file=sys.stderr)
        return 3
    print(f"OK: {n} NF-e processadas; relatorios em {args.dir_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
