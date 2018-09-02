module TrashPage.Update exposing (..)

import Result
import Time

import Graphqelm.Http
import Graphqelm.Operation exposing (RootQuery, RootMutation)
import Graphqelm.OptionalArgument exposing (..)
import Graphqelm.SelectionSet exposing (SelectionSet, with)

import Trash.Enum.Metric exposing (Metric (..))
import Trash.Query as Query
import Trash.Mutation as Mutation
import Trash.Scalar

import TrashPage.Model exposing (..)

gqlHost : String
gqlHost = "/graphql/"

type Msg =
    ChangeVolume String

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model = case msg of
    (ChangeVolume s) -> ( changeVolume s model, Cmd.none )

changeVolume : String -> Model -> Model
changeVolume txt model = if txt == ""
    then model
        |> setPageVolume Nothing
        |> setPageError Nothing
        |> setPageChanged False
    else case String.toFloat txt of
        (Err _) -> model
            |> setPageVolume Nothing
            |> setPageError (Just "Amount must be a number")
            |> setPageChanged True
        (Ok x) -> if x < 0
            then model
                |> setPageVolume Nothing
                |> setPageError (Just "Amount must be 0 or more")
                |> setPageChanged True
            else model
                |> setPageVolume (Just x)
                |> setPageError Nothing
                |> setPageChanged True
