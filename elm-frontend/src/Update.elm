module Update exposing (..)

import Result
import Time

import Graphqelm.Http
import Graphqelm.Operation exposing (RootMutation)
import Graphqelm.OptionalArgument exposing (..)
import Graphqelm.SelectionSet exposing (SelectionSet, with)

import Trash.Enum.Metric exposing (Metric (..))
import Trash.Mutation as Mutation
import Trash.Scalar

import Model exposing (..)

gqlHost : String
gqlHost = "/graphql/"

{-| Elm Messages |-}
type Msg =
    ChangeAmount String
    | SavePage
    | GotResponse (Result (Graphqelm.Http.Error Response) Response)

{-| Update |-}
update : Msg -> Model -> ( Model, Cmd Msg )
update msg model = case msg of
    (ChangeAmount s) -> ( changeAmount s model, Cmd.none )
    (GotResponse r) -> ( gotResponse r model, Cmd.none )
    SavePage -> ( model, savePage model )

changeAmount : String -> Model -> Model
changeAmount txt model = case String.toFloat txt of
    (Err _) ->
        if txt == ""
            then
                { model | volume = Nothing
                , error = Nothing
                , changed = True
                }
            else
                { model | volume = Nothing
                , error = Just "Amount must be a number"
                , changed = True
                }
    (Ok x) ->
        if x < 0
            then
                { model | volume = Nothing
                , error = Just "Amount must be 0 or more"
                , changed = True
                }
            else
                { model | volume = Just x, error = Nothing, changed = True }


-- Handle Responses

gotResponse : Result (Graphqelm.Http.Error Response) Response -> Model -> Model
gotResponse r model = case r of
    (Err err) ->
        { model | volume = Nothing
        , error = Just <| responseErrorMessage err
        }
    (Ok response) -> case response.trash of
        Nothing -> { model | volume = Nothing, error = Just "Failed to save!" }
        (Just trash) ->
            { model | volume = trashVolume trash model.metric, changed = False }

responseErrorMessage : Graphqelm.Http.Error Response -> String
responseErrorMessage error = case error of
    (Graphqelm.Http.HttpError err) -> toString err
    (Graphqelm.Http.GraphqlError _ errs) ->
        List.foldr (\err txt -> err.message ++ " " ++ txt) "" errs

trashVolume : Trash -> Metric -> Maybe Float
trashVolume trash metric = case metric of
    Gallons -> trash.gallons
    Litres -> trash.litres

-- GraphQL Mutation

savePage : Model -> Cmd Msg
savePage model =
    mutation
            model.jwt
            (relativeDate model.timestamp model.day)
            model.metric
            model.volume
    |> Graphqelm.Http.mutationRequest gqlHost
    |> Graphqelm.Http.send GotResponse


mutation : Jwt -> Trash.Scalar.Date -> Metric -> Maybe Float ->
           SelectionSet Response RootMutation
mutation jwt date metric maybeVol =
    let volume = case maybeVol of
        Nothing -> Absent
        (Just x) -> Present x
    in Mutation.selection Response
    |> with ( Mutation.saveTrash
        (\opts ->
            { opts | metric = Present metric
            , volume = volume
            }
        )
        { token = jwtString jwt, date = date }
        trashField
    )
