module UpdateTrashPage exposing (..)

import GraphQL.Request.Builder exposing (..)
import GraphQL.Request.Builder.Arg as Arg
import GraphQL.Request.Builder.Variable as Var
import GraphQL.Client.Http as GraphQLClient

import Date exposing (fromString, fromTime)
import Result
import Task exposing (Task)

import Models exposing (..)

type Msg = ChangeAmount String | NewTrash Trash | NewError String

{-| Handle Elm Messages |-}
updateTrashPage : Msg -> TrashPage -> (TrashPage, Cmd Msg)
updateTrashPage msg model = case msg of
    (ChangeAmount txt) -> (changeAmount txt model, Cmd.none)
    (NewTrash trash) -> (newTrash trash model, Cmd.none)
    (NewError err) -> (newError err model, Cmd.none)

{-| When the user inputs a new amount of trash, update the amount or error
    message as appropriate |-}
changeAmount : String -> TrashPage -> TrashPage
changeAmount txt page = case String.toFloat txt of
    (Err _) -> { page | error = Just "Amount must be a number" }
    (Ok x) ->
        if x < 0 then { page | error = Just "Amount must be 0 or more" }
        else { page | error = Just "... remember to save your changes!"
                    , trash = Just <| setAmount x
                                   <| Maybe.withDefault emptyTrash page.trash
             }

{-| Produce Trash with the updated amount |-}
setAmount : Float -> Trash -> Trash
setAmount x trash = case trash.amount of
    (Litres _) -> { trash | amount = Litres x }
    (Gallons _) -> { trash | amount = Gallons x }

{-| Replace the Trash with one recieved from the GraphQL |-}
newTrash : Trash -> TrashPage -> TrashPage
newTrash trash page = { page | trash = Just trash, error = Nothing }

{-| Replace the error with one recieved from the GraphQL |-}
newError : String -> TrashPage -> TrashPage
newError err page = { page | error = Just err }

{-| Submit the token and Trash info to the GraphQL interface for saving |-}
saveTrash : String -> Trash -> Cmd Msg
saveTrash token trash =
    let dateString = toString (Date.year trash.date) ++ "-"
                     ++ toString (Date.month trash.date) ++ "-"
                     ++ toString (Date.day trash.date)
        emptyInput = { token = token, date = dateString
                       , gallons = Nothing , litres = Nothing }
        input = case trash.amount of
            (Gallons x) -> { emptyInput | gallons = Just x }
            (Litres x)  -> { emptyInput | litres = Just x }
    in
        saveTrashGQL
        |> request input
        |> GraphQLClient.sendMutation "/graphql/?"
        |> Task.attempt recieveTrashNode

-- Graphql helpers --

{-| GraphQL arguments for the SaveTrash query |-}
type alias TrashInput =
    { token : String
    , date : String
    , gallons : Maybe Float
    , litres : Maybe Float
    }

{-| Conversion from GraphQL to Trash.  If there's a more direct way to get
    union types, dates, etc. I'd like to know |-}
type alias TrashNode =
    { date : String
    , gallons : Maybe Float
    , litres : Maybe Float
    }

{-| Convert the TrashNode to the Trash |-}
nodeToTrash : TrashNode -> Trash
nodeToTrash node =
    let amount = case node.gallons of
            (Just x) -> Gallons x
            Nothing -> Litres <| Maybe.withDefault 0 node.litres
        date = Result.withDefault (fromTime 0) (fromString node.date)
    in
        Trash date amount

{-| Builds the GraphQL query |-}
saveTrashGQL : Document Mutation TrashNode TrashInput
saveTrashGQL =
    let
        token = Var.required "token" .token Var.string
        date = Var.required "date" .date Var.string
        gallons = Var.required "gallons" .gallons (Var.nullable Var.float)
        litres = Var.required "litres" .litres (Var.nullable Var.float)

        -- decodes the response
        trashNode = object TrashNode
            |> with (field "date" [] string)
            |> with (field "gallons" [] (nullable float))
            |> with (field "litres" [] (nullable float))

        mutationRoot =
            extract
                (field "saveTrash"
                    [ ( "token", Arg.variable token )
                    , ( "date", Arg.variable date )
                    , ( "gallons", Arg.variable gallons )
                    , ( "litres", Arg.variable litres )
                    ]
                    trashNode
                )
    in mutationDocument mutationRoot

recieveTrashNode : Result GraphQLClient.Error TrashNode -> Msg
recieveTrashNode result = case result of
    Err (GraphQLClient.HttpError err) -> NewError (toString err)
    Err (GraphQLClient.GraphQLError err) -> NewError (toString err)
    Ok trashNode -> NewTrash (nodeToTrash trashNode)
