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

{-| Elm Messages |-}
type Msg =
    ChangeAmount String
    -- | LookupPage
    -- | GotResponseLookup
    --     (Result (Graphqelm.Http.Error ResponseLookup) ResponseLookup)
    -- | SavePage
    -- | GotResponseSave (Result (Graphqelm.Http.Error ResponseSave) ResponseSave)

{-| Update |-}
update : Msg -> Model -> ( Model, Cmd Msg )
update msg model = case msg of
    (ChangeAmount s) -> ( changeAmount s model, Cmd.none )
    -- LookupPage -> ( model, lookupPage model )
    -- (GotResponseLookup r) -> ( gotResponseLookup r model, Cmd.none )
    -- SavePage -> ( model, savePage model )
    -- (GotResponseSave r) -> ( gotResponseSave r model, Cmd.none )

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

gotResponseLookup : Result (Graphqelm.Http.Error ResponseLookup) ResponseLookup
                    -> Model -> Model
gotResponseLookup r model = case r of
    (Err err) ->
        { model | volume = Nothing
        , error = Just <| responseErrorMessage err
        }
    (Ok response) ->
        let newVolume =
            case response.trash of
                Nothing -> Nothing
                (Just trash) -> trashVolume trash model.metric
            statsPPPW = case model.metric of
                Gallons -> response.stats.gallonsPerPersonPerWeek
                Litres -> response.stats.litresPerPersonPerWeek
        in
            { model
            | volume = newVolume
            , changed = False
            , stats = { perPersonPerWeek = statsPPPW }
            }

gotResponseSave : Result (Graphqelm.Http.Error ResponseSave) ResponseSave
                  -> Model -> Model
gotResponseSave r model = case r of
    (Err err) ->
        { model | volume = Nothing
        , error = Just <| responseErrorMessage err
        }
    (Ok response) -> case response.trash of
        Nothing -> { model | volume = Nothing, error = Just "Failed to save!" }
        (Just trash) ->
            { model | volume = trashVolume trash model.metric, changed = False }

responseErrorMessage : Graphqelm.Http.Error a -> String -- ResponseSave -> String
responseErrorMessage error = case error of
    (Graphqelm.Http.HttpError err) -> toString err
    (Graphqelm.Http.GraphqlError _ errs) ->
        List.foldr (\err txt -> err.message ++ " " ++ txt) "" errs

trashVolume : Trash -> Metric -> Maybe Float
trashVolume trash metric = case metric of
    Gallons -> trash.gallons
    Litres -> trash.litres

-- GraphQL

lookupPage : Model -> Cmd Msg
lookupPage model =
    lookupQuery model.jwt (relativeDate model.timestamp model.day)
    |> Graphqelm.Http.queryRequest gqlHost
    |> Graphqelm.Http.send GotResponseLookup

lookupQuery : Jwt -> Trash.Scalar.Date -> SelectionSet ResponseLookup RootQuery
lookupQuery jwt date =
    let token = jwtString jwt
    in Query.selection ResponseLookup
        |> with ( Query.trash { token = token, date = date } trash )
        |> with ( Query.stats { token = token } stats )

savePage : Model -> Cmd Msg
savePage model =
    mutation
            model.jwt
            (relativeDate model.timestamp model.day)
            model.metric
            model.volume
    |> Graphqelm.Http.mutationRequest gqlHost
    |> Graphqelm.Http.send GotResponseSave

mutation : Jwt -> Trash.Scalar.Date -> Metric -> Maybe Float ->
           SelectionSet ResponseSave RootMutation
mutation jwt date metric maybeVol =
    let volume = case maybeVol of
        Nothing -> Absent
        (Just x) -> Present x
    in Mutation.selection ResponseSave
    |> with ( Mutation.saveTrash
        (\opts ->
            { opts | metric = Present metric
            , volume = volume
            }
        )
        { token = jwtString jwt, date = date }
        saveTrashField
    )
